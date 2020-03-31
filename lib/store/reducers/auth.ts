import { createReducer } from "typesafe-actions";

import { Tokens } from "../../models/Tokens";
import * as actions from "./../actions/auth";

export type AuthState = Readonly<{
  tokens: Tokens;
  loginErrorMessage: string;
}>;

const initialState: AuthState = {
  tokens: null,
  loginErrorMessage: "",
};

const authReducer = createReducer(initialState)
  .handleAction(actions.loginError, (state, action) => ({
    ...state,
    loginErrorMessage: action.payload,
  }))
  .handleAction(actions.loginSuccess, (state, action) => ({
    ...state,
    tokens: action.payload,
    loginErrorMessage: "",
  }))
  .handleAction(actions.logout, (state, action) => ({
    ...state,
    tokens: null,
  }))
  .handleAction(actions.authError, state => ({
    ...state,
    tokens: null,
  }));

export default authReducer;
