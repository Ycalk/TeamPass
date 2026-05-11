import { useEffect, useState } from 'react';
import {
  getMyTeam,
  getMe,
  getUserInvitations,
} from "../../api/teams";

import { NoTeamView } from './NoTeamView';
import { TeamView } from './TeamView';

export const Team = () => {
  const [loading, setLoading] = useState(true);
  const [team, setTeam] = useState<any>(null);
  const [isCaptain, setIsCaptain] = useState(false);
  const [invitations, setInvitations] = useState([]);

  const load = async () => {
    try {
      const teamRes = await getMyTeam();

      if (teamRes.status === 404) {
        setTeam(null);

        const invites =
          await getUserInvitations();

        setInvitations(invites.data);

        return;
      }

      const meRes = await getMe();

      setTeam(teamRes.data);

      setIsCaptain(
        teamRes.data.captain.id ===
          meRes.data.id
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (!team) {
    return (
      <NoTeamView
        invitations={invitations}
        onReload={load}
      />
    );
  }

  return (
    <TeamView
      team={team}
      isCaptain={isCaptain}
      onReload={load}
    />
  );
};