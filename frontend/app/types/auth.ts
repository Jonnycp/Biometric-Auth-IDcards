export interface LivenessProbabilities {
  real: number;
  print: number;
  screen: number;
}

export interface UserData {
  fullName: string;
  score: number;
  embedding: number[];
  createdAt: string;
}

export interface LoginMatchResponse {
  status: "MATCH" | "NO_MATCH";
  attack_type: string;
  similarity: number;
  liveness_score: number;
  liveness_probabilities: LivenessProbabilities;
  liveness_threshold: number;
  similarity_threshold: number;
  vector_score: number;
  embedding_score: number;
  user: UserData | null;
}

export interface LoginSpoofResponse {
  status: "SPOOF_ATTACK";
  attack_type: "PRINT" | "SCREEN" | "NONE" | "CROP FAILED" | string;
  liveness_score: number;
  liveness_probabilities: LivenessProbabilities;
  liveness_threshold: number;
  liveness_progress?: number;
}

export interface LoginWaitingFaceResponse {
  status: "WAITING_FACE";
  message: string;
}

export interface LoginWaitingLivenessResponse {
  status: "WAITING_LIVENESS";
  liveness_score: number;
  liveness_probabilities: LivenessProbabilities;
  liveness_threshold: number;
  liveness_progress: number;
}

export interface LoginErrorResponse {
  status: "ERROR";
  message: string;
}

export type LoginWSMessage =
  | LoginMatchResponse
  | LoginSpoofResponse
  | LoginWaitingFaceResponse
  | LoginWaitingLivenessResponse
  | LoginErrorResponse;

export interface RegisterResponse {
  message: string;
  user: UserData | null;
  score: number;
  fixProspective: boolean;
  fixContrast: boolean;
}
