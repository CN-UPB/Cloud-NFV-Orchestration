import axios, { AxiosError } from "axios";

import { Descriptor } from "./../models/Descriptor";
import { Service } from "./../models/Service";
import { ApiReply } from "../models/ApiReply";
import { getApiUrl } from "./index";

/**
 * Sends a onboard request to the API
 *
 * @param id The id of the service descriptor to be onboarded
 */
export async function onboardServiceDescriptor(id: string): Promise<ApiReply<Service>> {
  try {
    const reply = await axios.post(getApiUrl("services"), { id });
    return { success: true, payload: reply.data };
  } catch (error) {
    switch ((error as AxiosError).response?.status) {
      case 400:
        return {
          success: false,
          message: (error as AxiosError).response.data.detail,
        };
      case 401:
        return { success: false, message: "Unauthorized" };
      default:
        return { success: false, message: "An unexpected error occurred. Please try again." };
    }
  }
}
