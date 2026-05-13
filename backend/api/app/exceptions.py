class BusinessValidationError(Exception):
    """Domain-level validation error for business rules.

    Services should raise this when a business invariant is violated.
    Controllers translate it to an HTTP 400 response.
    """
    pass