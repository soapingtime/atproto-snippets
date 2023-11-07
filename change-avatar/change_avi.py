import os
import random

from atproto import Client, models
from atproto.exceptions import BadRequestError


def main():
    client = Client()
    client.login(os.environ['BSKY_HANDLE'], os.environ['BSKY_APP_PASSWORD'])

    try:
        current_profile_record = client.com.atproto.repo.get_record(
            models.ComAtprotoRepoGetRecord.Params(
                collection=models.ids.AppBskyActorProfile,
                repo=client.me.did,
                rkey='self',
            )
        )
        current_profile = current_profile_record.value
        swap_record_cid = current_profile_record.cid
    except BadRequestError:
        current_profile = swap_record_cid = None

    old_description = old_display_name = None
    if current_profile:
        old_description = current_profile.description
        old_display_name = current_profile.display_name


    # update with new layout
    avatar_dir = "pfps"
    random_avatar = random.choice(os.listdir(avatar_dir))
    avatar_path = os.path.join(avatar_dir, random_avatar)

    print("using", avatar_path)
    with open(avatar_path, 'rb') as f:
        img_data = f.read()
        upload = client.com.atproto.repo.upload_blob(img_data)

        client.com.atproto.repo.put_record(
            models.ComAtprotoRepoPutRecord.Data(
                collection=models.ids.AppBskyActorProfile,
                repo=client.me.did,
                rkey='self',
                swap_record=swap_record_cid,
                record=models.AppBskyActorProfile.Main(
                    avatar=upload.blob,                # current_profile.avatar to keep old avatar. to set a new one, you should upload blob first
                    banner=current_profile.banner,     # keep old banner. to set a new one, you should upload blob first
                    description=old_description,
                    display_name=old_display_name,
                ),
            )
        )


if __name__ == '__main__':
    main()
