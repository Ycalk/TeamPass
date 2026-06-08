import { apiClient } from './client';

export const getListings = () =>
  apiClient.get('/market/listings');

export const getMyListings = () =>
  apiClient.get('/market/listings/my');

export const getTokens = () =>
  apiClient.get('/market/listings/tokens');

export const createListing = (
  title: string,
  description: string
) =>
  apiClient.post('/market/listings', {
    title,
    description,
  });

export const createResponse = (
  listingId: string
) =>
  apiClient.post('/market/responses', {
    market_listing_id: listingId,
  });

export const getListingResponses = (
  listingId: string
) =>
  apiClient.get(
    `/market/listings/${listingId}/responses`
  );

export const createDeal = (
  responseId: string
) =>
  apiClient.post('/market/deals', {
    response_id: responseId,
  });

export const getListingDeal = (
  listingId: string
) =>
  apiClient.get(
    `/market/listings/${listingId}/deal`
  );

export const getMyResponses = () =>
  apiClient.get('/market/responses/my');

export const getResponseDeal = (
  responseId: string
) =>
  apiClient.get(
    `/market/responses/${responseId}/deal`
  );

export const getDealReport = (
  dealId: string
) =>
  apiClient.get(
    `/market/deals/${dealId}/report`,
    { skipGlobalErrorNotification: true } as any
  );

export const createDealReport = (
  dealId: string,
  content: any
) =>
  apiClient.post(
    `/market/deals/${dealId}/report`,
    {
      deal_id: dealId,
      content,
    }
  );

export const updateDealReport = (
  dealId: string,
  content: any
) =>
  apiClient.patch(
    `/market/deals/${dealId}/report`,
    {
      deal_id: dealId,
      content,
    }
  );

export const completeDeal = (
  dealId: string
) =>
  apiClient.post(
    `/market/deals/${dealId}/complete`
  );