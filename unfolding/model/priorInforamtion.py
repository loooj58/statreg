from ..interface import IPriorInformation


class ParametricPrior(IPriorInformation):
    """
  For different types of parametric prior information, a la:
    .. math:: \int \langle \varphi,\hat{\Omega}\varphi \rangle P(\varphi) d\varphi = \omega

    Parameter:
    .. math:: \alpha = \alpha(\omega)

    """
    alpha = None
    omega = None


