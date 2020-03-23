from connexion.exceptions import BadRequestProblem, ProblemException


class NotFoundProblem(ProblemException):
    def __init__(self, title='Not Found', detail=None):
        super(NotFoundProblem, self).__init__(status=404, title=title, detail=detail)


class InvalidDescriptorContentError(BadRequestProblem):
    """
    Indicates that invalid content has been assigned to `Descriptor.descriptor`
    """

    def __init__(self, detail, **kwargs):
        super(InvalidDescriptorContentError, self).__init__(
            title="Invalid Descriptor",
            detail=detail,
            **kwargs
        )


class DuplicateDescriptorError(BadRequestProblem):
    def __init__(self, **kwargs):
        super(DuplicateDescriptorError, self).__init__(
            title="Duplicate Descriptor",
            detail="A descriptor with the given vendor, name, and version " +
            "does already exist in the database.",
            **kwargs
        )


class DescriptorNotFoundError(NotFoundProblem):
    def __init__(self, detail="No descriptor matching the given id was found.", **kwargs):
        super(DescriptorNotFoundError, self).__init__(
            title="Descriptor Not Found",
            detail=detail,
            **kwargs
        )


class ServiceNotFoundError(NotFoundProblem):
    def __init__(self, detail="No service matching the given id was found.", **kwargs):
        super(ServiceNotFoundError, self).__init__(
            title="Service Not Found",
            detail=detail,
            **kwargs
        )
