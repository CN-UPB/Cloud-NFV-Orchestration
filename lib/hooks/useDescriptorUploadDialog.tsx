import { Button } from "@material-ui/core";
import yaml from "js-yaml";
import * as React from "react";
import { useModal } from "react-modal-hook";
import { useDispatch } from "react-redux";

import { uploadDescriptor } from "../api/descriptors";
import { FileSelector } from "../components/content/FileSelector";
import { GenericDialog } from "../components/layout/dialogs/GenericDialog";
import { DescriptorType } from "../models/Descriptor";
import { showInfoDialog, showSnackbar } from "../store/actions/dialogs";

export function useDescriptorUploadDialog(descriptorType: DescriptorType) {
  const dispatch = useDispatch();

  const acceptedFiles = []; //Cannot get this to only allow for .yaml files upload
  /**
   * Display a dialog for uploading Descriptors...
   */
  let yamlFile, parsedYamlFile;
  let type = descriptorType;

  function onDrop(files) {
    const blb = new Blob([files], { type: "text/yaml" });
    var file = new File([blb], "descriptor", { type: "text/yaml;charset=utf-8" });
    const reader = new FileReader();

    reader.onload = (e) => {
      //text contains the file contents as is.
      var fileText = reader.result.toString();
      yamlFile = fileText;
      parsedYamlFile = yaml.safeLoad(fileText);
    };

    // Start reading the blob as text.
    reader.readAsText(file);
  }

  async function upload() {
    hideFileSelector();

    /**
     * Upload descriptor type, parsedYamlFile, File with the API
     */
    const reply = await uploadDescriptor(type, parsedYamlFile, yamlFile);
    if (reply.success) {
      dispatch(showSnackbar("Descriptor successfully uploaded"));
      refreshWindow();
    } else {
      dispatch(showInfoDialog({ title: "Error Infomation", message: reply.message }));
    }
  }

  function refreshWindow() {
    window.location.reload(false);
  }

  const [showFileSelector, hideFileSelector] = useModal(({ in: open, onExited }) => (
    <GenericDialog
      dialogId="uploader"
      dialogTitle="Pishahang Descriptor Uploader"
      open={open}
      onExited={onExited}
      onClose={hideFileSelector}
      buttons={
        <>
          <Button variant="contained" onClick={upload} color="primary" autoFocus>
            Upload
          </Button>
        </>
      }
    >
      <FileSelector
        acceptedFiles={acceptedFiles}
        maxFileSize={10}
        showPreviews={false}
        showAlerts={true}
        filesLimit={1}
        dropzoneText={"Drag or Click"}
        onDrop={onDrop}
        showFileNames={true}
      ></FileSelector>
    </GenericDialog>
  ));

  return function showDescriptorUploadDialog() {
    showFileSelector();
  };
}
