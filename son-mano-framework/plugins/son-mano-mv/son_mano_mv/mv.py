"""
Copyright (c) 2015 SONATA-NFV
ALL RIGHTS RESERVED.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.
This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the SONATA
partner consortium (www.sonata-nfv.eu).a
"""

import logging
import yaml
import time
import os
import requests
import copy
import uuid
import json
import threading
import sys
import csv
import concurrent.futures as pool
# from multi_version import CreateTemplate
from son_mano_mv.multi_version import CreateTemplate

# import psutil
try:
    from son_mano_mv import mv_helpers as tools
except:
    import mv_helpers as tools

from sonmanobase.plugin import ManoBasePlugin


logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("plugin:mv")
LOG.setLevel(logging.INFO)


class MVPlugin(ManoBasePlugin):
    """
    This class implements the Multiversion Plugin.
    """

    def __init__(self,
                 auto_register=True,
                 wait_for_registration=True,
                 start_running=True):
        """
        Initialize class and son-mano-base.plugin.BasePlugin class.
        This will automatically connect to the broker, contact the
        plugin manager, and self-register this plugin to the plugin
        manager.

        After the connection and registration procedures are done, the
        'on_lifecycle_start' method is called.
        :return:
        """

        # call super class (will automatically connect to
        # broker and register the Placement plugin to the plugin manger)
        ver = "0.1-dev"
        des = "This is the Multiversion plugin"

        self.mon_metrics = {}
        # TODO: Make is consistant
        self.active_services = {}

        super(self.__class__, self).__init__(version=ver,
                                             description=des,
                                             auto_register=auto_register,
                                             wait_for_registration=wait_for_registration,
                                             start_running=start_running)

    def __del__(self):
        """
        Destroy Placement plugin instance. De-register. Disconnect.
        :return:
        """
        super(self.__class__, self).__del__()

    def declare_subscriptions(self):
        """
        Declare topics that Placement Plugin subscribes on.
        """
        # We have to call our super class here
        super(self.__class__, self).declare_subscriptions()

        # The topic on which deploy requests are posted.
        topic = 'mano.service.place'
        mv_mon_topic = 'mano.service.mv_mon'
        self.manoconn.subscribe(self.mon_request, mv_mon_topic)
        self.manoconn.subscribe(self.placement_request, topic)

        LOG.info("Subscribed to topic: " + str(topic))

    def on_lifecycle_start(self, ch, mthd, prop, msg):
        """
        This event is called when the plugin has successfully registered itself
        to the plugin manager and received its lifecycle.start event from the
        plugin manager. The plugin is expected to do its work after this event.

        :param ch: RabbitMQ channel
        :param method: RabbitMQ method
        :param properties: RabbitMQ properties
        :param message: RabbitMQ message content
        :return:
        """
        super(self.__class__, self).on_lifecycle_start(ch, mthd, prop, msg)
        LOG.info("Placement plugin started and operational.")

    def deregister(self):
        """
        Send a deregister request to the plugin manager.
        """
        LOG.info('Deregistering Placement plugin with uuid ' + str(self.uuid))
        message = {"uuid": self.uuid}
        self.manoconn.notify("platform.management.plugin.deregister",
                             json.dumps(message))
        os._exit(0)

    def on_registration_ok(self):
        """
        This method is called when the Placement plugin
        is registered to the plugin mananger
        """
        super(self.__class__, self).on_registration_ok()
        LOG.debug("Received registration ok event.")

    def remove_empty_values(self, line):
        """
        remove empty values (from multiple delimiters in a row)
        :param line: Receives the Line
        :return: sends back after removing the empty value
        """
        result = []
        for i in range(len(line)):
            if line[i] != "":
                result.append(line[i])
        return result


##########################
# Placement
##########################


    def mon_request(self, ch, method, prop, payload):
        """
        This method handles a MV Monitoringrequest
        """
        if prop.app_id == self.name:
            return

        content = yaml.load(payload)
        serv_id = content['serv_id']

        LOG.info("MV MON request for service: " + serv_id)
        # LOG.info(content)

        if content['request_type'] == "START":
            is_nsd = content['is_nsd']
            self.active_services[serv_id] = {}
            self.active_services[serv_id]['charts'] = []
            self.active_services[serv_id]['vim_endpoint'] = ""
            self.active_services[serv_id]['function_versions'] = content['function_versions']
            self.active_services[serv_id]['version_changed'] = False
            topology = content['topology']
            functions = content['functions'] if 'functions' in content else []
            cloud_services = content['cloud_services'] if 'cloud_services' in content else []
            
            if is_nsd:
                for _function in functions:
                    for _vdu in _function['vnfr']['virtual_deployment_units']:
                        for _vnfi in _vdu['vnfc_instance']:
                            # LOG.info(_vnfi)
                            for _t in topology:
                                # LOG.info(_t)
                                if _t['vim_uuid'] == _vnfi['vim_id']:
                                    LOG.info("VNF is on")
                                    LOG.info(_vnfi['vim_id'])
                                    _instance_id = tools.get_nova_server_info(serv_id, _t)
                                    _charts = tools.get_netdata_charts(_instance_id, _t)
                                    LOG.info(_instance_id)
                                    LOG.info(len(_charts))
                                    self.active_services[serv_id]['charts'] = _charts
                                    self.active_services[serv_id]['vim_endpoint'] = _t['vim_endpoint']
                                    self.active_services[serv_id]['metadata'] = content
                                    self.active_services[serv_id]['is_nsd'] = is_nsd                                    
            else:
                LOG.info("Not OpenStack monitoting")
                for _function in cloud_services:
                    for _vdu in _function['csr']['virtual_deployment_units']:
                        # LOG.info(_vnfi)
                        for _t in topology:
                            # LOG.info(_t)
                            if _t['vim_uuid'] == _vdu['vim_id']:
                                LOG.info("VNF is on")
                                LOG.info(_vdu['vim_id'])
                                LOG.info(_t['vim_endpoint'])
                                # FIXME: Timer for creation delay (Add a loop?)
                                time.sleep(10)
                                _instance_id = tools.get_k8_pod_info(serv_id, _t)
                                _charts = tools.get_netdata_charts(_instance_id, _t)
                                LOG.info(_instance_id)
                                LOG.info(_charts)
                                self.active_services[serv_id]['charts'] = _charts
                                self.active_services[serv_id]['vim_endpoint'] = _t['vim_endpoint']
                                self.active_services[serv_id]['metadata'] = content
                                self.active_services[serv_id]['is_nsd'] = is_nsd

        elif content['request_type'] == "STOP":
            self.active_services.pop(serv_id, None)
            LOG.info("Monitoring stopped")

        else:
            LOG.info("Request type not suppoted")


    def request_version_change(self, serv_id, time_vm=6, time_acc=0.25):
            MV_CHANGE_VERSION = "mano.instances.change"
            content = self.active_services[serv_id]['metadata']
            content['function_versions'] = self.active_services[serv_id]['function_versions']
            content['time_vm'] = time_vm
            content['time_acc'] = time_acc

            self.manoconn.call_async(self.handle_resp_change,
                                    MV_CHANGE_VERSION,
                                    yaml.dump(content))


    def handle_resp_change(self):
        LOG.info("MV Handle Change Request ")

    def placement_request(self, ch, method, prop, payload):
        """
        This method handles a placement request
        """

        if prop.app_id == self.name:
            return

        content = yaml.load(payload)

        # FIXME: This should be calculated based on mintoring thread
        ### SD: Time in system for requests (consists of actual computation time + waiting time of flows within the function)
        self.mon_metrics["time_vm"] = content['time_vm'] # Change it to 60 to get as_accelerated component in the result file 
        self.mon_metrics["time_acc"] = content['time_acc']

        #  calls create_template to create the template from the payload and returns created result file.
        _template_generator = CreateTemplate.TemplateGenerator(content, self.mon_metrics)
        result_data = _template_generator.create_template()

        LOG.info("MV request for service: " + content['serv_id'])
        topology = content['topology']
        descriptor = content['nsd']
        functions = content['functions']

        placement = self.placement(descriptor, functions, topology, result_data)

        response = {'mapping': placement}
        topic = 'mano.service.place'

        self.manoconn.notify(topic,
                             yaml.dump(response),
                             correlation_id=prop.correlation_id)

        LOG.info("MV response sent for service: " + content['serv_id'])
        # LOG.info(response)

    def placement(self, descriptor, functions, topology, result_data):
        """
        This is the default placement algorithm that is used if the SLM
        is responsible to perform the placement
        """
        LOG.info("MV Embedding started on following topology: " + str(topology))

        as_vm, as_container, as_accelerated = result_data["as_vm"], result_data["as_container"], result_data["as_accelerated"]
        vnf_name_id_mapping = CreateTemplate.get_name_id_mapping(descriptor)

        if "S" in as_vm: as_vm.remove("S")

        # LOG.info("\n\nas_vm: ", str(as_vm), "\n\nas_container: ", str(as_container), "\n\nas_accelerated: ", str(as_accelerated))

        LOG.info("as_vm")
        LOG.info(as_vm)
        LOG.info("as_container")
        LOG.info(as_container)
        LOG.info("as_accelerated")
        LOG.info(as_accelerated)

        mapping = {}
        mapping_counter = 0
        # FIXME: designed only for 1
        is_nsd = True

        if len(as_vm) > 0:
            # FIXME: should support multiple VDU?
            cloud_services = []
            LOG.info("VM Mapping")
            for function in functions:
                vnfd = function['vnfd']
                vdu = vnfd['virtual_deployment_units']
                vnf_id = CreateTemplate.get_function_id(vnfd['name'], vnf_name_id_mapping)
                needed_cpu = vdu[0]['resource_requirements']['cpu']['vcpus']
                needed_mem = vdu[0]['resource_requirements']['memory']['size']
                needed_sto = vdu[0]['resource_requirements']['storage']['size']

                for vim in topology:
                    if vim['vim_type'] == 'Heat':
                        for as_vm_function in as_vm:
                            if vnf_id in as_vm_function:
                                cpu_req = needed_cpu <= (vim['core_total'] - vim['core_used'])
                                mem_req = needed_mem <= (vim['memory_total'] - vim['memory_used'])

                                if cpu_req and mem_req:
                                    function["vim_uuid"] = vim['vim_uuid']
                                    vim['core_used'] = vim['core_used'] + needed_cpu
                                    vim['memory_used'] = vim['memory_used'] + needed_mem
                                    mapping_counter += 1
                                    break

        elif len(as_accelerated) > 0:
            # FIXME: should support multiple VDU?
            LOG.info("Accelerated Mapping")
            cloud_services = functions
            functions = []

            for cloud_service in cloud_services:
                cloud_service['csd'] = cloud_service['vnfd']
                cloud_service['csd']['virtual_deployment_units'] = cloud_service['vnfd']['virtual_deployment_units_acc']
                csd = cloud_service['csd']

                vdu = csd['virtual_deployment_units']
                needed_mem = 0
                if 'resource_requirements' in vdu[0] and 'memory' in vdu[0]['resource_requirements']:
                    needed_mem = vdu[0]['resource_requirements']['memory']['size']

                for vim in topology:

                    # For our use case, we use kubernetes for accelerated images
                    if vim['vim_type'] != 'Kubernetes':
                        continue
                    mem_req = needed_mem <= (vim['memory_total'] - vim['memory_used'])

                    if mem_req:
                        cloud_service["vim_uuid"] = vim['vim_uuid']
                        vim['memory_used'] = vim['memory_used'] + needed_mem
                        mapping_counter += 1
                        is_nsd = False
                        break


        mapping["functions"] = functions
        mapping["cloud_services"] = cloud_services
        mapping["is_nsd"] = is_nsd

        # LOG.info("Functions \n\n\n")
        # LOG.info(functions)

        # LOG.info("Cloud_services \n\n\n")
        # LOG.info(cloud_services)

        # LOG.info("Mapping \n\n\n")
        # LOG.info(mapping)

        # Check if all VNFs and CSs have been mapped
        if mapping_counter == len(functions) + len(cloud_services):
            return mapping
        else:
            LOG.info("Placement was not possible")
            return None

        return mapping


    def run(self):
        while(True):
            LOG.info("\nSLM Thread\n")
            try:
                for _service, _service_meta in self.active_services.items():
                    LOG.info("\n\n ########################## \n\n")

                    LOG.info(_service)
                    _metrics = tools.get_netdata_charts_instance(_service_meta['charts'], _service_meta['vim_endpoint'])
                    # LOG.info(json.dumps(_metrics, indent=4, sort_keys=True))
                    LOG.info("### CPU ###")
                    LOG.info(_metrics["cpu"])
                    LOG.info("### BANDWIDTH ###")
                    LOG.info(_metrics["bandwidth"])

                    # TODO: map bandwidth with time
                    # 1080 ~ 2GB per hour ~ 30 MB per min
                    # Let's say the VNF can handle avg 60MB per min, otherwise switch
                    # wget -O /dev/null http://speedtest.belwue.net/100M

                    if not self.active_services[_service]['version_changed']:
                        try:
                            if _metrics["bandwidth"]['data'][0][1] >= 30:
                                LOG.info("### BANDWIDTH Limit reached ###")
                                # FIXME: need to identify vm or acc or what is deployed already
                                self.active_services[_service]['version_changed'] = True
                                self.request_version_change(_service, time_vm=60, time_acc=0.25)
                        except Exception as e:
                            LOG.error("Monitoring still not active")

                    LOG.info("\n\n ########################## \n\n")

            except Exception as e:
                LOG.error("SLM Thread Error")
                LOG.error(e)

            time.sleep(10)


def main():
    """
    Entry point to start plugin.
    :return:
    """
    # reduce messaging log level to have a nicer output for this plugin
    logging.getLogger("son-mano-base:messaging").setLevel(logging.INFO)
    logging.getLogger("son-mano-base:plugin").setLevel(logging.INFO)
#    logging.getLogger("amqp-storm").setLevel(logging.DEBUG)
    # create our function lifecycle manager
    placement = MVPlugin()

if __name__ == '__main__':
    main()
