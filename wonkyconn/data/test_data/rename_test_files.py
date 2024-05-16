from pathlib import Path
import json

atlas_collection = "Schaefer20187Networks"
denoise = "Simple"
giga_connectome_output = Path(__file__).parent / "connectome_Schaefer20187Networks_dev"


# rename the files
files = giga_connectome_output.glob("sub-*/ses-*/func/*")

for file in files:
    root = file.name.split("space-")[0]
    root_with_space = file.name.split("atlas-")[0]
    atlas = file.name.split("atlas-")[-1]
    suffix = file.name.split("_")[-1]
    atlas = atlas.split("_")[0]
    subject_dir = file.parent

    if "json" in suffix:
        # make up some content for the json file
        meta = {
            "MeanFramewiseDisplacement": 0.03,
            "ConfoundRegressors": ["csf", "white_matter", "grey_matter","cosine00", "cosine01", "cosine02", "cosine03", "trans_x", "trans_y", "trans_z", "rot_x", "rot_y", "rot_z"],
            "NumberOfVolumesDiscardedByMotionScrubbing": 0,
            "NumberOfVolumesDiscardedByNonsteadyStatesDetector": 5,
        }
        # load the json file
        with open(file, "r") as f:
            old_meta = json.load(f)
        meta.update(old_meta)
        # update the json file with the new meta data
        with open(file, "w") as f:
            json.dump(meta, f)

    if "desc" not in file.name:
        new_name = f"{root}desc-denoise{denoise}_{suffix}"
    else:
        n_parcel, denoise_strategy = file.name.split("desc-")[1].split("7Networks")
        denoise_strategy = denoise_strategy.split("_")[0]
        seg = atlas + n_parcel
        desc = denoise_strategy
        if "meas" in file.name:
            meas = file.name.split("meas-")[1].split("_")[0]
            new_name = f"{root}seg-{seg}_meas-{meas}_desc-denoise{desc}_{suffix}"
        else:
            new_name = f"{root}seg-{seg}_desc-denoise{desc}_{suffix}"

    file.rename(subject_dir / new_name)

# rename the working_dir
(giga_connectome_output / "working_dir").rename(giga_connectome_output / "atlases")
(giga_connectome_output / "atlases" / "groupmasks").rename(giga_connectome_output / "atlases" / "sub-1")
(giga_connectome_output / "atlases" / "sub-1" / "tpl-MNI152NLin2009cAsym" ).rename(giga_connectome_output / "atlases" / "sub-1" / "func")
working_dir = giga_connectome_output / "atlases" / "sub-1" / "func"

# working_dir = giga_connectome_output / "working_dir" / "groupmasks" / "tpl-MNI152NLin2009cAsym"
files = working_dir.glob("*.nii.gz")
sub = root_with_space.split("_")[0]
space = root_with_space.split("space-")[-1].split("_")[0]
res = root_with_space.split("res-")[-1].split("_")[0]
root_with_space = f"{sub}_space-{space}_res-{res}"

for file in files:
    suffix = file.name.split("_")[-1]
    if "atlas" in file.name:
        atlas = file.name.split("atlas-")[1].split("_")[0]
        n_parcel = file.name.split("desc-")[1].split("7Networks")[0]
        seg = atlas + n_parcel
        new_name = f"{sub}_seg-{seg}_{suffix}"
    else:
        new_name = file.name.replace("tpl-MNI152NLin2009cAsym", root_with_space)
        new_name = new_name.replace("_res-dataset", "")
        new_name = new_name.replace("_desc-group", "")
    file.rename(working_dir / new_name)
    # print(new_name)
