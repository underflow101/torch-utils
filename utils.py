#####################################################################
# utils.py
#
# Dev. Dongwon Paek
# Description: Util source code of SqueezeNet
#####################################################################


import os, time, datetime
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

from model import SqueezeNet


class Solver(object):
    DEFAULTS = {}
    def __init__(self, data_loader, config):
        # data loader
        self.__dict__.update(Solver.DEFAULTS, **config)
        self.data_loader = data_loader

        self.build_model()

    def build_model(self):
        # instantiate model
        self.model = SqueezeNet(self.input_channels, self.class_count)

        # instantiate loss criterion
        self.criterion = nn.CrossEntropyLoss()

        # instantiate optimizer
        self.optimizer = optim.SGD(self.model.parameters(), lr=self.lr, momentum=self.momentum, weight_decay=self.weight_decay)

        # print network
        self.print_network(self.model, 'SqueezeNet')

        # use gpu if enabled
        if torch.cuda.is_available() and self.use_gpu:
            self.model.cuda()
            self.criterion.cuda()

    def print_network(self, model, name):
        num_params = 0
        for p in model.parameters():
            num_params += p.numel()
        print(name)
        print(model)
        print("The number of parameters: {}".format(num_params))

    def print_loss_log(self, start_time, iters_per_epoch, e, i, loss):
        total_iter = self.num_epochs * iters_per_epoch
        cur_iter = e * iters_per_epoch + i

        elapsed = time.time() - start_time
        total_time = (total_iter - cur_iter) * elapsed / (cur_iter + 1)
        epoch_time = (iters_per_epoch - i) * elapsed / (cur_iter + 1)

        epoch_time = str(datetime.timedelta(seconds=epoch_time))
        total_time = str(datetime.timedelta(seconds=total_time))
        elapsed = str(datetime.timedelta(seconds=elapsed))

        log = "Elapsed {}/{} -- {}, Epoch [{}/{}], Iter [{}/{}], " \
              "loss: {:.4f}".format(elapsed, epoch_time, total_time, e + 1, self.num_epochs, i + 1, iters_per_epoch, loss)
        print(log)

    def save_model(self, e):
        path = os.path.join(
            self.model_save_path,
            '{}.pth'.format(e + 1)
        )

        torch.save(self.model.state_dict(), './')

    def model_step(self, images, labels):
        # set model in training mode
        self.model.train()

        # empty the gradients of the model through the optimizer
        self.optimizer.zero_grad()

        # forward pass
        output = self.model(images)

        # compute loss
        loss = self.criterion(output, labels.squeeze())

        # compute gradients using back propagation
        loss.backward()

        # update parameters
        self.optimizer.step()

        return loss

    def train(self):
        self.losses = []
        self.top_1_acc = []
        self.top_5_acc = []

        iters_per_epoch = len(self.data_loader)

        # start with a trained model if exists
        if self.pretrained_model:
            start = int(self.pretrained_model.split('/')[-1])
        else:
            start = 0

        # start training
        start_time = time.time()
        for e in range(start, self.num_epochs):
            for i, (images, labels) in enumerate(tqdm(self.data_loader)):
                images = to_var(images, self.use_gpu)
                labels = to_var(labels, self.use_gpu)

                loss = self.model_step(images, labels)

            # print out loss log
            if (e + 1) % self.loss_log_step == 0:
                self.print_loss_log(start_time, iters_per_epoch, e, i, loss)
                self.losses.append((e, loss))

            # save model
            if (e + 1) % self.model_save_step == 0:
                self.save_model(e)

            # evaluate on train dataset
            if (e + 1) % self.train_eval_step == 0:
                top_1_acc, top_5_acc = self.train_evaluate(e)
                self.top_1_acc.append((e, top_1_acc))
                self.top_5_acc.append((e, top_5_acc))

        # print losses
        print('\n--Losses--')
        for e, loss in self.losses:
            print(e, '{:.4f}'.format(loss))

        # print top_1_acc
        print('\n--Top 1 accuracy--')
        for e, acc in self.top_1_acc:
            print(e, '{:.4f}'.format(acc))

        # print top_5_acc
        print('\n--Top 5 accuracy--')
        for e, acc in self.top_5_acc:
            print(e, '{:.4f}'.format(acc))

    def eval(self, data_loader):
        # set the model to eval mode
        self.model.eval()

        top_1_correct = 0
        top_5_correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in data_loader:

                images = to_var(images, self.use_gpu)
                labels = to_var(labels, self.use_gpu)

                output = self.model(images)
                total += labels.size()[0]

                # top 1
                # get the max for each instance in the batch
                _, top_1_output = torch.max(output.data, dim=1)

                top_1_correct += torch.sum(torch.eq(labels.squeeze(),
                                                    top_1_output))

                # top 5
                _, top_5_output = torch.topk(output.data, k=5, dim=1)
                for i, label in enumerate(labels):
                    if label in top_5_output[i]:
                        top_5_correct += 1

        return top_1_correct.item(), top_5_correct, total

    def train_evaluate(self, e):
        """
        Evaluates the performance of the model using the train dataset
        """
        top_1_correct, top_5_correct, total = self.eval(self.data_loader)
        log = "Epoch [{}/{}]--top_1_acc: {:.4f}--top_5_acc: {:.4f}".format(
            e + 1,
            self.num_epochs,
            top_1_correct / total,
            top_5_correct / total
        )
        print(log)
        return top_1_correct / total, top_5_correct / total

    def test(self):
        """
        Evaluates the performance of the model using the test dataset
        """
        top_1_correct, top_5_correct, total = self.eval(self.data_loader)
        log = "top_1_acc: {:.4f}--top_5_acc: {:.4f}".format(
            top_1_correct / total,
            top_5_correct / total
        )
        print(log)
        
def to_var(x, use_gpu, requires_grad=False):
    if torch.cuda.is_available() and use_gpu:
        x = x.cuda()
    x.requires_grad = requires_grad
    return x