import torch
import torch.nn as nn


class BiFPN(nn.Module):
    def __init__(self,
                 num_channels):
        super(BiFPN, self).__init__()
        self.num_channels = num_channels
        self.input_image = 512
        self.top_down = [
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
        ]
        self.down = [
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
            nn.Conv2d(in_channels=self.num_channels, out_channels=self.num_channels,
                      kernel_size=3, padding=1, groups=self.num_channels),
        ]

    def forward(self, inputs):
        num_channels = self.num_channels
        P3_in, P4_in, P5_in, P6_in, P7_in = inputs

        P7_up = self.top_down[0](P7_in)
        scale = int(P6_in.size(3)/P7_up.size(3))
        P6_up = self.top_down[1](
            P6_in + self.Resize(scale_factor=scale)(P7_up))
        scale = int(P5_in.size(3)/P6_up.size(3))
        P5_up = self.top_down[2](
            P5_in + self.Resize(scale_factor=scale)(P6_up))
        scale = int(P4_in.size(3)/P5_up.size(3))
        P4_up = self.top_down[3](
            P4_in + self.Resize(scale_factor=scale)(P5_up))
        scale = int(P3_in.size(3)/P4_up.size(3))
        P3_out = self.top_down[4](
            P3_in + self.Resize(scale_factor=scale)(P4_up))

        kernel_size = int(P3_out.size(3)/P4_up.size(3))
        P4_out = self.down[0](
            P4_in+P4_up+nn.MaxPool2d(kernel_size=kernel_size)(P3_out))
        kernel_size = int(P4_out.size(3)/P5_up.size(3))
        P5_out = self.down[1](
            P5_in+P5_up+nn.MaxPool2d(kernel_size=kernel_size)(P4_out))
        kernel_size = int(P5_out.size(3)/P6_up.size(3))
        P6_out = self.down[2](
            P6_in+P6_up+nn.MaxPool2d(kernel_size=kernel_size)(P5_out))
        kernel_size = int(P6_out.size(3)/P7_up.size(3))
        P7_out = self.down[3](
            P7_in+P7_up+nn.MaxPool2d(kernel_size=kernel_size)(P6_out))
        return P3_out, P4_out, P5_out, P6_out, P7_out

    @staticmethod
    def Conv(in_channels, out_channels, kernel_size, stride, padding, groups=1):
        features = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=out_channels,
                      kernel_size=kernel_size, stride=stride, padding=padding, groups=groups),
            nn.BatchNorm2d(num_features=out_channels),
            nn.ReLU()
        )
        return features

    @staticmethod
    def Resize(scale_factor=2, mode='nearest'):
        upsample = nn.Upsample(scale_factor=scale_factor, mode=mode)
        return upsample
