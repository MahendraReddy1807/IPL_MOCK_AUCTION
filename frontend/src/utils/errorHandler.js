/**
 * Error handling utilities for the frontend
 */

/**
 * Extract error message from various error formats
 * @param {*} error - Error object from API or other sources
 * @returns {string} User-friendly error message
 */
export const getErrorMessage = (error) => {
  // Check if it's an Axios error with response
  if (error.response) {
    // Server responded with error status
    if (error.response.data) {
      if (error.response.data.message) {
        return error.response.data.message
      }
      if (typeof error.response.data === 'string') {
        return error.response.data
      }
    }
    
    // Fallback to status text
    return error.response.statusText || 'An error occurred'
  }
  
  // Check if it's a network error
  if (error.request) {
    return 'Network error. Please check your connection.'
  }
  
  // Check if it's a standard Error object
  if (error.message) {
    return error.message
  }
  
  // Fallback for unknown error types
  if (typeof error === 'string') {
    return error
  }
  
  return 'An unexpected error occurred'
}

/**
 * Get error code from error object
 * @param {*} error - Error object
 * @returns {string|null} Error code or null
 */
export const getErrorCode = (error) => {
  if (error.response && error.response.data && error.response.data.code) {
    return error.response.data.code
  }
  return null
}

/**
 * Check if error is a validation error
 * @param {*} error - Error object
 * @returns {boolean} True if validation error
 */
export const isValidationError = (error) => {
  const code = getErrorCode(error)
  return code && (
    code.includes('VALIDATION') ||
    code.includes('INVALID') ||
    code === 'BAD_REQUEST'
  )
}

/**
 * Check if error is a network error
 * @param {*} error - Error object
 * @returns {boolean} True if network error
 */
export const isNetworkError = (error) => {
  return error.request && !error.response
}

/**
 * Check if error is an authentication error
 * @param {*} error - Error object
 * @returns {boolean} True if authentication error
 */
export const isAuthError = (error) => {
  return error.response && (
    error.response.status === 401 ||
    error.response.status === 403
  )
}

/**
 * Format error for display
 * @param {*} error - Error object
 * @returns {Object} Formatted error with title and message
 */
export const formatError = (error) => {
  const message = getErrorMessage(error)
  const code = getErrorCode(error)
  
  let title = 'Error'
  
  if (isValidationError(error)) {
    title = 'Validation Error'
  } else if (isNetworkError(error)) {
    title = 'Connection Error'
  } else if (isAuthError(error)) {
    title = 'Access Denied'
  } else if (error.response && error.response.status >= 500) {
    title = 'Server Error'
  }
  
  return {
    title,
    message,
    code
  }
}

/**
 * Log error to console (can be extended to send to logging service)
 * @param {*} error - Error object
 * @param {string} context - Context where error occurred
 */
export const logError = (error, context = '') => {
  const errorInfo = formatError(error)
  console.error(`[${context}]`, errorInfo, error)
  
  // TODO: Send to error tracking service (e.g., Sentry)
}

/**
 * Handle API errors with user-friendly messages
 * @param {*} error - Error object
 * @param {Function} setError - State setter for error message
 * @param {string} context - Context for logging
 */
export const handleApiError = (error, setError, context = '') => {
  logError(error, context)
  const errorInfo = formatError(error)
  setError(errorInfo.message)
}

/**
 * Validation helper for form inputs
 */
export const validators = {
  /**
   * Validate username
   * @param {string} username - Username to validate
   * @returns {string|null} Error message or null if valid
   */
  username: (username) => {
    if (!username || username.trim().length === 0) {
      return 'Username cannot be empty'
    }
    if (username.length > 50) {
      return 'Username must be 50 characters or less'
    }
    return null
  },
  
  /**
   * Validate team name
   * @param {string} teamName - Team name to validate
   * @returns {string|null} Error message or null if valid
   */
  teamName: (teamName) => {
    if (!teamName || teamName.trim().length === 0) {
      return 'Team name cannot be empty'
    }
    if (teamName.length > 100) {
      return 'Team name must be 100 characters or less'
    }
    return null
  },
  
  /**
   * Validate room code
   * @param {string} roomCode - Room code to validate
   * @returns {string|null} Error message or null if valid
   */
  roomCode: (roomCode) => {
    if (!roomCode || roomCode.trim().length === 0) {
      return 'Room code cannot be empty'
    }
    return null
  },
  
  /**
   * Validate purse amount
   * @param {number} purse - Purse amount to validate
   * @returns {string|null} Error message or null if valid
   */
  purse: (purse) => {
    if (purse === null || purse === undefined || purse === '') {
      return 'Purse amount is required'
    }
    const amount = parseFloat(purse)
    if (isNaN(amount)) {
      return 'Purse must be a valid number'
    }
    if (amount <= 0) {
      return 'Purse must be a positive number'
    }
    if (amount > 10000) {
      return 'Purse amount is too large'
    }
    return null
  },
  
  /**
   * Validate file upload
   * @param {File} file - File to validate
   * @param {Array<string>} allowedTypes - Allowed MIME types
   * @param {number} maxSize - Max file size in bytes
   * @returns {string|null} Error message or null if valid
   */
  file: (file, allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'], maxSize = 5 * 1024 * 1024) => {
    if (!file) {
      return 'No file selected'
    }
    if (!allowedTypes.includes(file.type)) {
      return `File type must be one of: ${allowedTypes.join(', ')}`
    }
    if (file.size > maxSize) {
      return `File size must be less than ${maxSize / (1024 * 1024)}MB`
    }
    return null
  }
}
