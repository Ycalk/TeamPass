import { apiClient } from "./client";

const api = apiClient;

//
// TEAMS
//

export const getMyTeam = async () => {
  return api.get("/teams/me", {
    validateStatus: (status) =>
      status === 200 || status === 404,
  });
};

export const createTeam = async (name: string) => {
  return api.post("/teams", {
    name,
  });
};

export const changeTeamName = async (name: string) => {
  return api.patch("/teams/me/name", {
    name,
  });
};

export const transferCaptaincy = async (
  userId: string
) => {
  return api.patch("/teams/me/captaincy", {
    new_captain_id: userId,
  });
};

export const removeMember = async (
  memberId: string
) => {
  return api.delete(
    `/teams/me/members/${memberId}`
  );
};

export const leaveTeam = async () => {
  return api.delete("/teams/me/members/me");
};

//
// INVITATIONS
//

export const getUserInvitations = async () => {
  return api.get("/teams/invitations");
};

export const acceptInvitation = async (
  invitationId: string
) => {
  return api.post(
    `/teams/invitations/${invitationId}`
  );
};

export const declineInvitation = async (
  invitationId: string
) => {
  return api.delete(
    `/teams/invitations/${invitationId}`
  );
};

export const getTeamInvitations = async () => {
  return api.get("/teams/me/invitations");
};

export const sendInvitation = async (
  userId: string
) => {
  return api.post("/teams/me/invitations", {
    invited_user_id: userId,
  });
};

export const deleteTeamInvitation = async (
  invitationId: string
) => {
  return api.delete(
    `/teams/invitations/${invitationId}`
  );
};

//
// USERS
//

export const getMe = async () => {
  return api.get("/users/me");
};

export const searchUsers = async (
  query: string
) => {
  return api.get("/users/search", {
    params: {
      query,
    },
  });
};