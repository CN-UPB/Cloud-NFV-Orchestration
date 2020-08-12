import { BaseEntity } from "./BaseEntity";

export enum DescriptorType {
  Service = "service",
  OPENSTACK = "openStack",
  KUBERNETES = "kubernetes",
  AWS = "aws",
}

/**
 * Virtual network function descriptor definition – VM, CN, or FPGA-based
 */
export interface DescriptorContent {
  descriptor_version: string;
  name: string;
  vendor: string;
  version: string;
  description?: string;
  author?: string;
}

/**
 * Descriptor type as used by the API
 */
export interface Descriptor extends BaseEntity {
  type: DescriptorType;
  content: DescriptorContent;
}
