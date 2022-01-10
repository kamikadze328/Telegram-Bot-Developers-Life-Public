from strsimpy.normalized_levenshtein import NormalizedLevenshtein

import Image

levenshtein = NormalizedLevenshtein()


def find_most_similar(request_str, images) -> Image:
    dictionary = {}
    for i in images:
        description = i.description.decode("utf-8")
        image = Image.Image(description=description,
                            filename=i.local_path.decode("utf-8"),
                            service_id=i.service_id,
                            distance=levenshtein.distance(request_str, description))
        dictionary[image.filename] = image
    return min(dictionary.items(), key=lambda x: x[1].distance)[1]
