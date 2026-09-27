import type { ApiErrorResponse } from "@/types/api"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000"

export class ApiError extends Error {
  readonly status: number
  readonly data: ApiErrorResponse | null

  constructor(
    message: string,
    status: number,
    data: ApiErrorResponse | null = null,
  ) {
    super(message)

    this.name = "ApiError"
    this.status = status
    this.data = data
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const headers = new Headers(options.headers)

  headers.set("Accept", "application/json")

  let body: BodyInit | undefined

  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json")
    body = JSON.stringify(options.body)
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,
      headers,
      body,
    },
  )

  if (!response.ok) {
    const errorData =
      await parseErrorResponse(response)

    throw new ApiError(
      getErrorMessage(
        errorData,
        response.status,
      ),
      response.status,
      errorData,
    )
  }

  if (
    response.status === 204 ||
    response.headers.get("content-length") === "0"
  ) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export function apiGet<T>(
  endpoint: string,
  signal?: AbortSignal,
): Promise<T> {
  return apiRequest<T>(
    endpoint,
    {
      method: "GET",
      signal,
    },
  )
}

async function parseErrorResponse(
  response: Response,
): Promise<ApiErrorResponse | null> {
  try {
    return await response.json() as ApiErrorResponse
  } catch {
    return null
  }
}

function getErrorMessage(
  data: ApiErrorResponse | null,
  status: number,
): string {
  if (
    data &&
    typeof data.detail === "string"
  ) {
    return data.detail
  }

  if (
    data &&
    typeof data.detail === "object" &&
    data.detail !== null &&
    "message" in data.detail &&
    typeof data.detail.message === "string"
  ) {
    return data.detail.message
  }

  return `ToolFence API request failed with status ${status}.`
}

export {
  API_BASE_URL,
}
