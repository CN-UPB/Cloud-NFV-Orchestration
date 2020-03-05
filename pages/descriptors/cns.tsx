import Fab from "@material-ui/core/Fab";
import { CloudUpload, DateRange } from "@material-ui/icons";
import { SimpleFileUpload } from "formik-material-ui";
import { NextPage } from "next";

import { Page } from "../../lib/components/layout/Page";
import { VnfdTable } from "../../lib/components/layout/tables/VnfdTable";
import { useDescriptorUploadDialog } from "../../lib/hooks/useDescriptorUploadDialog";
import { DescriptorType } from "../../lib/models/descriptorType";
import { VnfdMeta } from "../../lib/models/VnfdMeta";

const ContainersPage: NextPage = () => {
  const showDescriptorUploadDialog = useDescriptorUploadDialog(DescriptorType.CN);

  const data: VnfdMeta[] = [
    {
      type: DescriptorType.CN,
      descriptor: {
        name: "forwarder-vm-vnf",
        vendor: "eu.sonata-nfv.cloud-service-descriptor",
        version: "1.0",
        author: "Elton John",
        description: "ICMP ping request forwarder; container-based VNF.",
        descriptor_version: "2.0",
        virtual_deployment_units: "",
      },
      id: "66695e0f-5472-4f85-a310-fe0676bf28e6",
    },
  ];

  return (
    <Page title="CN Based VNF Descriptors">
      <Fab
        color="primary"
        size="small"
        style={{ float: "right" }}
        aria-label="Upload"
        onClick={showDescriptorUploadDialog}
      >
        <CloudUpload />
      </Fab>
      <VnfdTable pageName="Container" data={data}></VnfdTable>
    </Page>
  );
};

export default ContainersPage;
