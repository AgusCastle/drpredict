import argparse
from unicodedata import name
from data_loader import LesionSegMask, ClassificationTest

from torch.utils.data import DataLoader
from drmodel import DeepDRModule, TrainEvalDataset
from save_info import Util
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--train_maskrcnn', action='store_true', default=False, help="train mask_rcnn")
    parser.add_argument('--train_classification', action='store_true', default=False,
                        help="train claffisication network")
    parser.add_argument('--data_root', default='data', help='root directory of the dataset')
    parser.add_argument('--with_maskrcnn', action='store_true', default=False,
                        help='whether to include the maskRCNN feature when training the classification network')

    parser.add_argument('--dump', default=None, help='where to save the snapshot of the network')
    parser.add_argument('--load_and_transfer', default=None, help='load the ')
    parser.add_argument('--load_all', default=None, help='load all weights')
    parser.add_argument('--load_maskrcnn', default=None, help='load maskrcnn weights')
    parser.add_argument('--load_classification', default=None, help='load classification weights')
    parser.add_argument('--test_classification', action='store_true', default=False, help="train mask_rcnn")
    parser.add_argument('--trainable_layers', default=5, type=int,
                        help='number of trainable (not frozen) resnet layers starting from final block.'
                             'Valid values are between 0 and 5, with 5 meaning all backbone layers are trainable.')
    parser.add_argument('--lr', default=0.001, type=float, help='learning rate')

    parser.add_argument('--device', default='cuda:0')

    parser.add_argument('--snap_db', default=None, help='snap_storage model, only in debug mode')
    parser.add_argument('--max_epoch', default=20, type=int, help='maximum epoch to train')
    parser.add_argument('--file_json', default=None)
    parser.add_argument('--clean_loss', action='store_true', default=False)
    parser.add_argument('--clean_preds', action='store_true', default=False)
    args = parser.parse_args()

    model = DeepDRModule(
        snap_storage=args.snap_db,
        device=args.device,
    )

    json_file = ''


    if args.file_json is not None:
        if not os.path.exists(args.file_json):
            Util.generarJSON(filename=args.file_json)
        json_file = args.file_json

    if args.clean_loss:
        Util.clean_loss(json_file)
    
    if args.clean_preds:
        Util.clean_preds(json_file)

    if args.load_all is not None:
        model.load_all(args.load_all)

    if args.load_maskrcnn is not None:
        model.load_maskrcnn(args.load_maskrcnn)

    if args.load_classification is not None:
        model.load_classification(args.load_classification)

    if args.load_and_transfer is not None:
        model.load_transfer(args.load_and_transfer)

    if args.train_maskrcnn:
        loader = DataLoader(
            TrainEvalDataset(
                LesionSegMask(split='train', root=args.data_root)),
            batch_size= 16,
            shuffle=False,
            num_workers=16)
        for _ in range(args.max_epoch):
            model.set_lr(args.lr)
            model.train_mask_rcnn_epoch(loader)

    if args.test_classification:
        loader = DataLoader(
            ClassificationTest(split='train', root=args.data_root),
            batch_size=1,
            shuffle=True,
            num_workers=1
        )
        model.test_classification(loader, json_file)

    if args.train_classification:
        loader = DataLoader(
            ClassificationTest(split='train', root=args.data_root),
            batch_size=16,
            shuffle=True,
            num_workers=8
        )
        for _ in range(args.max_epoch):
            model.set_lr(args.lr)
            loss = model.train_classification(loader, args.with_maskrcnn)
            Util.guardarLoss(filename=json_file, loss=loss)

            model.dump_classification(f'{args.dump}_last_classification.pkl')


    if args.dump is not None:
        model.dump_maskrcnn(f'{args.dump}_mask.pkl')
        model.dump_all(f'{args.dump}_model.pkl')
        model.dump_classification(f'{args.dump}_classification.pkl')
