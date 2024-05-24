from pathlib import Path
import sys
from PIL import Image
from utils_ootd import get_mask_location
import base64
from io import BytesIO
import requests

PROJECT_ROOT = Path(__file__).absolute().parents[1].absolute()
sys.path.insert(0, str(PROJECT_ROOT))

from preprocess.openpose.run_openpose import OpenPose
from preprocess.humanparsing.run_parsing import Parsing
from ootd.inference_ootd_hd import OOTDiffusionHD
from ootd.inference_ootd_dc import OOTDiffusionDC


openpose_model = OpenPose(0)
parsing_model = Parsing(0)


category_dict = ['upperbody', 'lowerbody', 'dress']
category_dict_utils = ['upper_body', 'lower_body', 'dresses']

model_type = "dc" # "hd" or "dc"

image_scale = 2.0
n_steps = 20
n_samples = 4
seed = 1

model = OOTDiffusionDC(0)

# category = args.category # 0:upperbody; 1:lowerbody; 2:dress
# cloth_path = args.cloth_path
# model_path = args.model_path

def predictTryOn(category, cloth_path, model_64):
    cloth_img = Image.open(BytesIO(requests.get(cloth_path).content)).resize((768, 1024))
    # model_img = Image.open(model_path).resize((768, 1024))
    
    person_bytes = base64.b64decode(model_64)
    person_file = BytesIO(person_bytes)
    model_img = Image.open(person_file)

    keypoints = openpose_model(model_img.resize((384, 512)))
    model_parse, _ = parsing_model(model_img.resize((384, 512)))

    mask, mask_gray = get_mask_location(model_type, category_dict_utils[category], model_parse, keypoints)
    mask = mask.resize((768, 1024), Image.NEAREST)
    mask_gray = mask_gray.resize((768, 1024), Image.NEAREST)

    masked_vton_img = Image.composite(mask_gray, model_img, mask)

    images = model(
        model_type=model_type,
        category=category_dict[category],
        image_garm=cloth_img,
        image_vton=masked_vton_img,
        mask=mask,
        image_ori=model_img,
        num_samples=n_samples,
        num_steps=n_steps,
        image_scale=image_scale,
        seed=seed,
    )
    tryImg = images[0]
    imFile = BytesIO()
    tryImg.save(imFile,format="JPEG")
    im_bytes = imFile.getvalue()
    im_64 = base64.b64encode(im_bytes)

    return im_64



# if __name__ == '__main__':

#     if model_type == 'hd' and category != 0:
#         raise ValueError("model_type \'hd\' requires category == 0 (upperbody)!")

#     cloth_img = Image.open(cloth_path).resize((768, 1024))
#     model_img = Image.open(model_path).resize((768, 1024))
#     keypoints = openpose_model(model_img.resize((384, 512)))
#     model_parse, _ = parsing_model(model_img.resize((384, 512)))

#     mask, mask_gray = get_mask_location(model_type, category_dict_utils[category], model_parse, keypoints)
#     mask = mask.resize((768, 1024), Image.NEAREST)
#     mask_gray = mask_gray.resize((768, 1024), Image.NEAREST)
    
#     masked_vton_img = Image.composite(mask_gray, model_img, mask)
#     masked_vton_img.save('./images_output/mask.jpg')

#     images = model(
#         model_type=model_type,
#         category=category_dict[category],
#         image_garm=cloth_img,
#         image_vton=masked_vton_img,
#         mask=mask,
#         image_ori=model_img,
#         num_samples=n_samples,
#         num_steps=n_steps,
#         image_scale=image_scale,
#         seed=seed,
#     )

#     image_idx = 0
#     for image in images:
#         image.save('./images_output/out_' + model_type + '_' + str(image_idx) + '.png')
#         image_idx += 1
