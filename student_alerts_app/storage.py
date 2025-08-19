from whitenoise.storage import CompressedManifestStaticFilesStorage

class CustomStaticFilesStorage(CompressedManifestStaticFilesStorage):
    def post_process(self, *args, **kwargs):
        # Generator to safely skip binary files that can't be decoded
        for name, hashed_name, processed in super().post_process(*args, **kwargs):
            try:
                yield name, hashed_name, processed
            except UnicodeDecodeError:
                # Skip problematic file
                print(f"Skipping file during collectstatic due to decode error: {name}")
                continue
