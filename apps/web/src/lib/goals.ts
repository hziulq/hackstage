import { apiClient } from "./api";
import type { components } from "./api-types.generated";

export type ApiGoal = components["schemas"]["Goal"];
export type ApiGoalMilestone = components["schemas"]["GoalMilestone"];

/** goals.py の /api/goals。current_user のものだけを対象にする(010-secure-social-api)。 */
export const goalsClient = {
  list: () => apiClient<ApiGoal[]>("/goals"),

  create: (input: { companyName: string; stage: string; targetDate: string }) =>
    apiClient<ApiGoal>("/goals", {
      method: "POST",
      body: JSON.stringify({
        company_name: input.companyName,
        stage: input.stage,
        target_date: input.targetDate,
      }),
    }),

  toggleMilestone: (goalId: number, milestoneId: number, done: boolean) =>
    apiClient<ApiGoalMilestone>(`/goals/${goalId}/milestones/${milestoneId}`, {
      method: "PATCH",
      body: JSON.stringify({ done }),
    }),

  remove: (goalId: number) => apiClient<void>(`/goals/${goalId}`, { method: "DELETE" }),
};
