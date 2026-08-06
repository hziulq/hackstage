import { apiClient } from "./api";
import type { components } from "./api-types.generated";

export type ApiReaction = components["schemas"]["Reaction"];

/** reactions.py の /api/reactions。 */
export const reactionsClient = {
  list: (targetType: ApiReaction["target_type"], targetId: number) =>
    apiClient<ApiReaction[]>(`/reactions?target_type=${targetType}&target_id=${targetId}`),

  create: (input: { targetType: ApiReaction["target_type"]; targetId: number; kind: ApiReaction["kind"] }) =>
    apiClient<ApiReaction>("/reactions", {
      method: "POST",
      body: JSON.stringify({
        target_type: input.targetType,
        target_id: input.targetId,
        kind: input.kind,
      }),
    }),

  remove: (reactionId: number) => apiClient<void>(`/reactions/${reactionId}`, { method: "DELETE" }),
};
