import type {
  FetchBuyOptions,
  FetchBuyQuote,
} from "@coinbase/cdp-react/components/Fund";

export const getBuyOptions: FetchBuyOptions = async (params) => {
  const queryParams = new URLSearchParams();
  queryParams.append("country", params.country);
  if (params?.subdivision) queryParams.append("subdivision", params.subdivision);

  const queryString = queryParams.toString();
  const url = `/api/onramp/buy-options${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || "Failed to fetch buy options");
  }

  return await response.json();
};

export const createBuyQuote: FetchBuyQuote = async (request) => {
  const response = await fetch("/api/onramp/buy-quote", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || "Failed to create buy quote");
  }

  return await response.json();
};
