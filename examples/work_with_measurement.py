import specatalog.data_management.hdf5_reader as hf
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


dat, file = hf.load_from_id(1, mode="a")

x = dat.raw_data.xaxis
intensity = dat.raw_data.data

plt.plot(x, np.real(intensity))
plt.plot(x, np.imag(intensity))


fit = -2*(x-12000)**2 + 25000

plt.plot(x, fit)

dat.evaluations.set_dataset("fit1", fit)

dat.sync()

figure_path = Path(file.filename).parent / "figures"

plt.savefig(figure_path / "fit_1.pdf")

file.close()
