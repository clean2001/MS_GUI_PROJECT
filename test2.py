import matplotlib.pyplot as plt
import spectrum_utils.plot as sup
import spectrum_utils.spectrum as sus

usi = "mzspec:PXD022531:j12541_C5orf38:scan:12368"
peptide = "VAATLEILTLK/2"
spectrum = sus.MsmsSpectrum.from_usi(usi)
spectrum.annotate_proforma(
    peptide,
    fragment_tol_mass=0.05,
    fragment_tol_mode="Da",
    ion_types="aby",
    max_ion_charge=2,
    neutral_losses={"NH3": -17.026549, "H2O": -18.010565},
)

fig, ax = plt.subplots(figsize=(10.5, 3))
sup.mass_errors(spectrum, plot_unknown=False, ax=ax)
plt.savefig("mass_errors.png", dpi=300, bbox_inches="tight", transparent=True)
plt.close()