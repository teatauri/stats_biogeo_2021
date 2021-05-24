import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..", "..")))

import time
import pickle
from alive_progress import alive_bar, config_handler
from pathlib import Path
from src.models import Save
from src.models.gams import TrainGams, MakePredictions
from src.views import PartialDepPlots

base_path = Path(os.path.abspath(__file__)).parents[2]

DATA = base_path / "data" / "processed"
RESULTS = base_path / "results" / "gams_output"
PLOTS = base_path / "results" / "all_plots"

config_handler.set_global(length=50, spinner="fish_bouncing")
t = time.sleep(2)


print("Obtaining plankton and predictor training datasets...")
with alive_bar(1) as bar:
    (plankton, plankton_r, plankton_f, plankton_rf,) = TrainGams.get_plankton(
        f"{DATA}/sampled_plankton",
        *[
            "plankton",
            "plankton_r",
            "plankton_f",
            "plankton_rf",
        ],
    )
    (predictors, predictors_r, predictors_f, predictors_rf,) = TrainGams.get_predictors(
        f"{DATA}/sampled_predictors",
        *[
            "predictors_X",
            "rand_predictors_X",
            "predictors_Xf",
            "rand_predictors_Xf",
        ],
    )
    bar()
    t


print("Fitting GAMs to sampled Darwin datasets (1987-2008) ...")
with alive_bar(2) as bar:
    plank_cut, plank_cut_r, plank_cut_f, plank_cut_rf = TrainGams.apply_cutoff(
        1.00e-5, *[plankton, plankton_r, plankton_f, plankton_rf]
    )
    bar()
    t
    gams_dict, gams_dict_r = TrainGams.fit_gams(
        *[
            [plankton, predictors],
            [plankton_r, predictors_r],
        ]
    )
    bar()
    t

print("Fitting GAMs on 2079-2100 samples to assess stability of relationships...")
with alive_bar(2) as bar:
    gams_dict_f, gams_dict_rf = TrainGams.fit_gams(
        *[
            [plankton_f, predictors_f],
            [plankton_rf, predictors_rf],
        ]
    )
    bar()
    t
    Save.save_gams(
        f"{RESULTS}/fitted_models",
        **{
            "gams_dict": gams_dict,
            "gams_dict_r": gams_dict_r,
            "gams_dict_f": gams_dict_f,
            "gams_dict_rf": gams_dict_rf,
        },
    )
    bar()
    t


print("Generating partial dependency plots...")
with alive_bar(2) as bar:
    PartialDepPlots.partial_dependency_plots(
        f"{PLOTS}/partial_dep_plots/from_measurements/",
        gams_dict,
        gams_dict_f,
    )
    bar()
    t
    PartialDepPlots.partial_dependency_plots(
        f"{PLOTS}/partial_dep_plots/from_random/",
        gams_dict_r,
        gams_dict_rf,
    )
    bar()
    t


print("Using GAMs from measurements to predict Darwin ocean biogeography (1987-2008)")
print("(Have a cup of tea - this could take a while...)")
with alive_bar(1) as bar:
    predictions_present = MakePredictions.make_predictions(
        plankton_gams_dict, f"{V_SETS}/predictors/ocean_X_present.pkl"
    )
    with open(f"{RESULTS}/predictions_present/test_predictions_p.pkl", "wb") as handle:
        pickle.dump(predictions_present, handle, protocol=pickle.HIGHEST_PROTOCOL)
    bar()
    t

# print(
#     "Using GAMs from random sampling to predict Darwin ocean biogeography (1987-2008)"
# )
# with alive_bar(1) as bar:
#     predictions_present_r = MakePredictions.make_predictions(
#         plankton_random_gams_dict, f"{V_SETS}/predictors/ocean_X_present.pkl"
#     )
#     with open(
#         f"{RESULTS}/predictions_present/test_predictions_random_p.pkl", "wb"
#     ) as handle:
#         pickle.dump(predictions_present_r, handle, protocol=pickle.HIGHEST_PROTOCOL)
#     bar()
#     t

# print("Using GAMs from measurements to predict Darwin ocean biogeography (2079-2100)")
# with alive_bar(1) as bar:
#     predictions_future = MakePredictions.make_predictions(
#         plankton_gams_dict, f"{V_SETS}/predictors/ocean_X_future.pkl"
#     )
#     with open(f"{RESULTS}/predictions_future/test_predictions_f.pkl", "wb") as handle:
#         pickle.dump(predictions_future, handle, protocol=pickle.HIGHEST_PROTOCOL)
#     bar()
#     t

# print(
#     "Using GAMs from random sampling to predict Darwin ocean biogeography (2079-2100)"
# )
# with alive_bar(1) as bar:
#     predictions_future_r = MakePredictions.make_predictions(
#         plankton_random_gams_dict, f"{V_SETS}/predictors/ocean_X_future.pkl"
#     )
#     with open(f"{RESULTS}/predictions_future/test_predictions_rf.pkl", "wb") as handle:
#         pickle.dump(predictions_future_r, handle, protocol=pickle.HIGHEST_PROTOCOL)
#     bar()
#     t
