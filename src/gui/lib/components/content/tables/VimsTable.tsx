import { useTheme } from "@material-ui/core";
import { Add, DeleteForeverRounded, Info } from "@material-ui/icons";
import React from "react";

import { ApiDataEndpoint } from "../../../api/endpoints";
import { useGenericConfirmationDialog } from "../../../hooks/genericConfirmationDialog";
import { useAddVimDialog } from "../../../hooks/useAddVimDialog";
import { useAuthorizedSWR } from "../../../hooks/useAuthorizedSWR";
import { ResourceUsageData, RetrievedVim, VimType } from "../../../models/Vim";
import { useThunkDispatch } from "../../../store";
import { showVimInfoDialog } from "../../../store/actions/dialogs";
import { deleteVim } from "../../../store/thunks/vims";
import { SwrDataTable } from "../../layout/tables/SwrDataTable";
import { VimTypeIconField } from "./fields/VimTypeIconField";

const formatResourceUsageData = (vim: RetrievedVim, resourceFieldName: string, unit?: string) => {
  if (vim.type == VimType.Aws) return "N/A";
  const usage: ResourceUsageData = vim.resourceUtilization[resourceFieldName];
  return `${usage.used}/${usage.total}` + (unit ? ` ${unit}` : "");
};

const projectResourceUsageData = (vim: RetrievedVim, resourceFieldName: string) => {
  if (vim.type == VimType.Aws) return 0;
  const usage: ResourceUsageData = vim.resourceUtilization[resourceFieldName];
  return usage.total - usage.used;
};

export const VimsTable: React.FunctionComponent = () => {
  const dispatch = useThunkDispatch();
  const swr = useAuthorizedSWR(ApiDataEndpoint.Vims);
  const showAddVimDialog = useAddVimDialog(swr.revalidate);
  const theme = useTheme();

  const showRemoveVimDialog = useGenericConfirmationDialog(
    "Remove VIM?",
    "Are you sure, you want to remove this VIM?",
    async (confirmed: boolean, id: string) => {
      if (!confirmed) return;

      let reply = await dispatch(deleteVim(id, { successSnackbarMessage: "VIM removed" }));
      if (reply.success) {
        swr.revalidate();
      }
    },
    "Remove VIM"
  );

  return (
    <SwrDataTable
      swr={swr}
      columns={[
        { title: "Name", field: "name" },
        {
          title: "Type",
          field: "type",
          render: (vim) => <VimTypeIconField vimType={vim.type} />,
        },
        { title: "Country", field: "country" },
        { title: "City", field: "city" },
        {
          title: "Core Usage",
          render: (vim) => formatResourceUsageData(vim, "cores"),
          customSort: (vim) => projectResourceUsageData(vim, "cores"),
        },
        {
          title: "Memory Usage",
          render: (vim) => formatResourceUsageData(vim, "memory", "MB"),
          customSort: (vim) => projectResourceUsageData(vim, "memory"),
        },
      ]}
      actions={[
        {
          icon: (props) => <Info htmlColor={theme.palette.primary.main} {...props} />,
          tooltip: "Info",
          onClick: (event, vim: RetrievedVim) => dispatch(showVimInfoDialog(vim)),
        },
        (vim) => ({
          icon: (props) => (
            <DeleteForeverRounded htmlColor={theme.palette.secondary.main} {...props} />
          ),
          tooltip: "Delete " + vim.name,
          onClick: () => showRemoveVimDialog(vim.id),
        }),
        {
          icon: (props) => <Add {...props} />,
          tooltip: "Add a VIM",
          onClick: showAddVimDialog,
          isFreeAction: true,
        },
      ]}
    />
  );
};
