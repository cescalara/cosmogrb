from gbmgeometry import GBM
import multiprocessing as mp


from cosmogrb.lightcurve import GBMLightCurve
from cosmogrb.sampler.source import Source
from cosmogrb.sampler.background import GBMBackground
from cosmogrb.sampler.cpl_source import CPLSourceFunction

from cosmogrb.sampler.constant_cpl import ConstantCPL

from cosmogrb.response import NaIResponse, BGOResponse


class GBMGRB(object):

    _background_start = -100
    _background_stop = 300
    _gbm_detectors = (
        "n0",
        "n1",
        "n2",
        "n3",
        "n4",
        "n5",
        "n6",
        "n7",
        "n8",
        "n9",
        "na",
        "nb",
        "b0",
        "b1",
    )

    def __init__(
        self,
        ra,
        dec,
        z,
        peak_flux,
        alpha,
        ep,
        tau,
        trise,
        duration,
        T0,
        name="SynthGRB",
        verbose=False,
    ):

        self._ra = ra
        self._dec = dec
        self._z = z
        self._alpha = alpha
        self._ep = ep
        self._trise = trise
        self._duration = duration
        self._name = name

        # self._cpl_source = ConstantCPL(peak_flux=peak_flux,
        #                                      trise=trise,
        #                                      tdecay=duration - trise,
        #                                      ep_tau=tau,
        #                                      alpha=alpha,
        #                                      ep_start=ep)

        # # self._cpl_source = CPLSourceFunction(peak_flux=peak_flux,
        # #                                      trise=trise,
        # #                                      tdecay=duration - trise,
        # #                                      ep_tau=tau,
        # #                                      alpha=alpha,
        # #                                      ep_start=ep)

        # self._source = Source(0., duration, self._cpl_source, use_plaw_sample=True)

        # self._source = Source(0., min(duration * 10., self._background_stop ), self._cpl_source, use_plaw_sample=True)

        self._lightcurves = []

        for det in self._gbm_detectors:

            if det[0] == "b":

                rsp = BGOResponse(det, ra, dec, T0, save=True, name=name)

            else:

                rsp = NaIResponse(det, ra, dec, T0, save=True, name=name)

            bkg = GBMBackground(
                self._background_start,
                self._background_stop,
                average_rate=500,
                detector=det,
            )

            cpl_source = ConstantCPL(
                peak_flux=peak_flux,
                trise=trise,
                tdecay=duration - trise,
                ep_tau=tau,
                alpha=alpha,
                ep_start=ep,
                response=rsp,
            )

            # self._cpl_source = CPLSourceFunction(peak_flux=peak_flux,
            #                                      trise=trise,
            #                                      tdecay=duration - trise,
            #                                      ep_tau=tau,
            #                                      alpha=alpha,
            #                                      ep_start=ep)

            source = Source(0.0, duration, cpl_source, use_plaw_sample=True)

            self._lightcurves.append(
                GBMLightCurve(
                    source, bkg, rsp, name=det, grb_name=self._name, verbose=verbose
                )
            )

    def go(self, n_cores=8):

        pool = mp.Pool(n_cores)

        pool.map(process_lightcurve, self._lightcurves)
        pool.close()
        pool.join()


def process_lightcurve(lc):
    lc.process()
    lc.write_tte()
