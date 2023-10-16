import { authenticatedRequest } from './index.js';

// A simple retry logic
const MAX_RETRIES = 3;

export const logMessage = async (
  level,
  message,
  module = 'UnknownModule',
  extra = {}, // Optional extra parameters
  retries = 0,
) => {
  try {
    const payload = {
      level,
      message,
      module,
      extra, // Include extra in the request payload
    };

    const response = await authenticatedRequest(
      'post',
      '/react_logging/',
      payload,
    );

    if (response.data.status === 'success') {
      // Success - No-Op or other handling
    } else if (retries < MAX_RETRIES) {
      // Retry logic
      await logMessage(level, message, module, extra, retries + 1);
    } else {
      // Fallback - could send a message to another logging service
    }
  } catch (error) {
    if (retries < MAX_RETRIES) {
      // Retry logic
      await logMessage(level, message, module, extra, retries + 1);
    } else {
      // Fallback - could send a message to another logging service
    }
  }
};
