import {
  IconButton,
  Paper,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
} from "@material-ui/core";
import { useTheme } from "@material-ui/core/styles";
import { InfoRounded, PlayCircleOutline } from "@material-ui/icons";
import React from "react";
import { useDispatch } from "react-redux";

import { User } from "../../../models/User";
import { showServiceInfoDialog, showSnackbar } from "../../../store/actions/dialogs";
import { formatDate } from "../../../util/time";
import { Table } from "../../layout/tables/Table";

type Props = {
  data: User[];
};

export const UsersTable: React.FunctionComponent<Props> = ({ data }) => {
  const theme = useTheme();
  const dispatch = useDispatch();

  function instantiateService() {
    dispatch(showSnackbar("Service instantiation not Implemented"));
  }

  return (
    <TableContainer component={Paper}>
      <Table aria-label="users table">
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell align="center">Vendor</TableCell>
            <TableCell align="center">Version</TableCell>
            <TableCell align="center">Onboarded at</TableCell>
            <TableCell align="center" style={{ width: "200px" }}>
              Actions
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((service) => (
            <TableRow key={service.name}>
              <TableCell component="th" scope="row">
                {service.name}
              </TableCell>
              <TableCell align="center">{service.vendor}</TableCell>
              <TableCell align="center">{service.version}</TableCell>
              <TableCell align="center">{formatDate(service.createdAt)}</TableCell>
              <TableCell align="center">
                <Tooltip title="Info" arrow>
                  <IconButton
                    color="primary"
                    onClick={() => dispatch(showServiceInfoDialog(service))}
                  >
                    <InfoRounded />
                  </IconButton>
                </Tooltip>
                <Tooltip title={"Instantiate " + service.name} arrow>
                  <IconButton onClick={() => instantiateService()}>
                    <PlayCircleOutline htmlColor={theme.palette.success.main} />
                  </IconButton>
                </Tooltip>
                {/* <Tooltip title={"Stop " + service.name} arrow>
                  <IconButton
                    color="primary"
                    onClick={() => showServiceStopDialog(service.id, service.name)}
                  >
                    <RadioButtonCheckedRounded htmlColor={theme.palette.error.main} />
                  </IconButton>
                </Tooltip> */}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
