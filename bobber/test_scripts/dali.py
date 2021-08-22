import os
import time
import torch
import nvidia.dali.types as types
import nvidia.dali.ops as ops
from argparse import ArgumentParser
from nvidia.dali.pipeline import Pipeline
from nvidia.dali.plugin.pytorch import DALIGenericIterator
from torch.utils.data import DistributedSampler


class ResNet50Pipeline(Pipeline):
    def __init__(self, batch_size, num_threads, device_id, images):
        super(ResNet50Pipeline, self).__init__(batch_size=batch_size,
                                               num_threads=num_threads,
                                               device_id=device_id)

        self.decoder = ops.decoders.Image(device='mixed', output_type=types.RGB)
        self.rrcp = ops.RandomResizedCrop(device='gpu', size=(224, 224))
        self.cmnp = ops.CropMirrorNormalize(device='gpu',
                                            dtype=types.FLOAT,
                                            output_layout=types.NCHW,
                                            crop=(224, 224),
                                            mean=[0.485 * 255, 0.456 * 255, 0.406 * 255],
                                            std=[0.229 * 225, 0.224 * 255, 0.225 * 255])
        self.random = ops.random.CoinFlip(probability=0.5)

    def base_graph(self, images):
        random = self.random()
        images = self.decoder(images)
        images = self.rrcp(images)
        images = self.cmnp(images.gpu(), mirror=random)
        return images


class FileReaderPipeline(ResNet50Pipeline):
    def __init__(self, **kwargs):
        super(FileReaderPipeline, self).__init__(**kwargs)

        self.reader = ops.readers.File(files=images,
                                       dont_use_mmap=True,
                                       stick_to_shard=False)

    def define_graph(self):
        images, _ = self.reader(name='Standard File Reader')
        return self.base_graph(images)


SUPPORTED_IMAGES = ('.jpg', '.jpeg', '.png')


def _image_dataset(directory: str) -> list:
    images = [os.path.join(directory, fn) for fn in os.listdir(directory)
              if fn.lower().endswith(SUPPORTED_IMAGES)]
    return images

torch.distributed.init_process_group(backend='nccl', init_method='env://')

images = _image_dataset('sample_images/test/')
local_images = DistributedSampler(images)
world_size = torch.distributed.get_world_size()

parser = ArgumentParser()
parser.add_argument('--local_rank', default=-1, type=int)
args = parser.parse_args()

pipe = FileReaderPipeline(batch_size=16, num_threads=3, device_id=args.local_rank, images=local_images)
pipe.build()

dali_iter = DALIGenericIterator(pipe, ['images'], size=len(local_images))

start = time.time()

for index, image in enumerate(dali_iter):
    pass

stop = time.time()

if args.local_rank == 0:
    local_throughput = len(local_images) / (stop - start)
    print(f'{round(local_throughput * world_size, 3)} images/second')
