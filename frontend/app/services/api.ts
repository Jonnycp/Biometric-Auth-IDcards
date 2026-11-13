import { getApiBaseUrl } from "../config";
import type { RegisterResponse } from "../types/auth";

export async function registerUserApi(
  fullName: string,
  idCardFile: File | Blob
): Promise<RegisterResponse> {
  const formData = new FormData();
  formData.append("fullName", fullName.trim());

  const fileName =
    idCardFile instanceof File ? idCardFile.name : "cie_document.jpg";
  formData.append("idCardImage", idCardFile, fileName);

  const baseUrl = getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/register`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = "Errore durante la registrazione.";
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = errorJson.detail;
      }
    } catch {
      // Ignora
    }
    throw new Error(errorDetail);
  }

  const data: RegisterResponse = await response.json();
  return data;
}
