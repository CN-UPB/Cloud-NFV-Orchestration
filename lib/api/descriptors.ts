import axios, { AxiosError, AxiosRequestConfig, AxiosResponse, Method } from "axios";

import { ApiReply } from "../models/ApiReply";
import { Descriptor } from "../models/Descriptor";
import { DescriptorType } from "../models/DescriptorType";
import { RegisterUser } from "../models/RegisterUser";
import { Session } from "../models/Session";
import { ApiDataEndpoint, ApiDataEndpointReturnType } from "./endpoints";
import { getApiUrl } from "./index";

/**
 * Sends a registration request to the API
 *
 *
 *
 * @returns An `ApiReply` object with a user-friendly error message in case of failure. In case of
 * success, the resulting `Session` object is provided via the `payload` attribute.
 */
export async function uploadDescriptor(
  descriptorType: DescriptorType,
  descriptorContent: any
): Promise<ApiReply> {
  try {
    const reply = await axios.post(getApiUrl("uploaded-descriptors"), {
      descriptor: descriptorContent,
      type: descriptorType,
    });
    window.location.reload(false);
    return { success: true };
  } catch (error) {
    switch ((error as AxiosError).response?.status) {
      case 401:
        return { success: false, message: "Invalid data" };
      default:
        return { success: false, message: "An unexpected error occurred. Please try again." };
    }
  }
}

/**
 * Fetches a descriptor based on the given UUID
 *
 *
 *
 * @returns An `ApiReply` object with a user-friendly error message in case of failure.
 */

export async function getDescriptor(uuid: String): Promise<ApiReply> {
  try {
    if (uuid == null) return;
    const reply = await axios.get(getApiUrl("uploaded-descriptors/" + uuid));
    window.location.reload(false);
    console.log(reply);

    return { success: true };
  } catch (error) {
    switch ((error as AxiosError).response?.status) {
      case 401:
        return { success: false, message: "Invalid data" };
      default:
        return { success: false, message: "An unexpected error occurred. Please try again." };
    }
  }
}

/**
 * Sends a deletion request to the API
 *
 *
 *
 * @returns An `ApiReply` object with a user-friendly error message in case of failure.
 */

export async function deleteDescriptor(uuid: String): Promise<ApiReply> {
  try {
    if (uuid == null) return;
    const reply = await axios.delete(getApiUrl("uploaded-descriptors/" + uuid));
    window.location.reload(false);
    console.log(uuid);

    return { success: true };
  } catch (error) {
    switch ((error as AxiosError).response?.status) {
      case 401:
        return { success: false, message: "Invalid data" };
      default:
        return { success: false, message: "An unexpected error occurred. Please try again." };
    }
  }
}

/**
 * Updates a descriptor with the given uuid
 *
 *
 *
 * @returns An `ApiReply` object with a user-friendly error message in case of failure.
 */

export async function updateDescriptor(
  descriptorContent: Descriptor,
  uuid: String
): Promise<ApiReply> {
  try {
    const reply = await axios.put(getApiUrl("uploaded-descriptors/" + uuid), {
      descriptor: descriptorContent,
    });

    window.location.reload(false);
    return { success: true };
  } catch (error) {
    switch ((error as AxiosError).response?.status) {
      case 401:
        return { success: false, message: "Invalid data" };
      default:
        return { success: false, message: "An unexpected error occurred. Please try again." };
    }
  }
}
