import torch
import torch.nn as nn
import torch.nn.functional as F
import config as cfg
import math


# --------------------------CNN-baseline-----------------------------
class CNN_baseline(nn.Module):
    def __init__(self):
        super(CNN_baseline, self).__init__()

        self.conv_layer = nn.Conv2d(in_channels=1, out_channels=5, kernel_size=(17,cfg.elenum), padding=(8, 0))
        self.relu = nn.ReLU()
        self.avg_pool = nn.AvgPool2d(kernel_size=(cfg.decision_window, 1))
        self.fc1 = nn.Linear(in_features=5, out_features=5)
        self.sigmoid = nn.Sigmoid()
        self.fc2 = nn.Linear(in_features=5, out_features=4)

    def forward(self, x):
        x = x.unsqueeze(dim=1)
        conv_out = self.conv_layer(x)
        relu_out = self.relu(conv_out)
        avg_pool_out = self.avg_pool(relu_out)
        flatten_out = torch.flatten(avg_pool_out, start_dim=1)
        fc1_out = self.fc1(flatten_out)
        sigmoid_out = self.sigmoid(fc1_out)
        fc2_out = self.fc2(sigmoid_out)

        return fc2_out


#-------------------------- STANet-------------------
# -------------------STAnet---------------------------

def transpose_qkv(X, num_heads):
    """Transposition for parallel computation of multiple attention heads.

    Defined in :numref:`sec_multihead-attention`"""
    # Shape of input `X`:
    # (`batch_size`, no. of queries or key-value pairs, `num_hiddens`).
    # Shape of output `X`:
    # (`batch_size`, no. of queries or key-value pairs, `num_heads`,
    # `num_hiddens` / `num_heads`)
    X = X.reshape(X.shape[0], X.shape[1], num_heads, -1)

    # Shape of output `X`:
    # (`batch_size`, `num_heads`, no. of queries or key-value pairs,
    # `num_hiddens` / `num_heads`)
    X = X.permute(0, 2, 1, 3)

    # Shape of `output`:
    # (`batch_size` * `num_heads`, no. of queries or key-value pairs,
    # `num_hiddens` / `num_heads`)
    return X.reshape(-1, X.shape[2], X.shape[3])


class DotProductAttention(nn.Module):
    """Scaled dot product attention.

    Defined in :numref:`subsec_additive-attention`"""

    def __init__(self, dropout, **kwargs):
        super(DotProductAttention, self).__init__(**kwargs)
        self.dropout = nn.Dropout(dropout)

    # Shape of `queries`: (`batch_size`, no. of queries, `d`)
    # Shape of `keys`: (`batch_size`, no. of key-value pairs, `d`)
    # Shape of `values`: (`batch_size`, no. of key-value pairs, value
    # dimension)

    def forward(self, queries, keys, values):
        d = queries.shape[-1]
        # Set `transpose_b=True` to swap the last two dimensions of `keys`
        scores = torch.bmm(queries, keys.transpose(1, 2)) / math.sqrt(d)
        self.attention_weights = nn.functional.softmax(scores, dim=-1)
        return torch.bmm(self.dropout(self.attention_weights), values)


def transpose_output(X, num_heads):
    """Reverse the operation of `transpose_qkv`.

    Defined in :numref:`sec_multihead-attention`"""
    X = X.reshape(-1, num_heads, X.shape[1], X.shape[2])
    X = X.permute(0, 2, 1, 3)
    return X.reshape(X.shape[0], X.shape[1], -1)


class MultiHeadAttention(nn.Module):
    """Multi-head attention.

    Defined in :numref:`sec_multihead-attention`"""

    def __init__(self, key_size, query_size, value_size, num_hiddens,
                 num_heads, dropout, bias=False, **kwargs):
        super(MultiHeadAttention, self).__init__(**kwargs)
        self.num_heads = num_heads
        self.attention = DotProductAttention(dropout)

        # 很奇怪，但没办法，就是这么定义的
        self.W_q = nn.Linear(query_size, num_hiddens * 10, bias=bias)
        self.W_k = nn.Linear(key_size, num_hiddens * 10, bias=bias)
        self.W_v = nn.Linear(value_size, num_hiddens, bias=bias)

    def forward(self, queries, keys, values):
        # Shape of `queries`, `keys`, or `values`:
        # (`batch_size`, no. of queries or key-value pairs, `num_hiddens`)

        # After transposing, shape of output `queries`, `keys`, or `values`:
        # (`batch_size` * `num_heads`, no. of queries or key-value pairs,
        # `num_hiddens` / `num_heads`)

        # 在我们的self_attention中，queries,keys,values都是X
        # transpose_qkv我们的目的是为了将X的最后一维分成num_heads份，然后将前两维交换，这样就可以并行计算，不必再去看源码了
        # 第一维会变成batch_size*num_heads，在我们的例子中，就是64*4=256
        # 也就是说，queries、keys、values都是(256,10,8)，第一维都是256，第二维是10，第三维是32/4=8
        queries = transpose_qkv(self.W_q(queries), self.num_heads)
        keys = transpose_qkv(self.W_k(keys), self.num_heads)
        values = transpose_qkv(self.W_v(values), self.num_heads)

        # Shape of `output`: (`batch_size` * `num_heads`, no. of queries,
        # `num_hiddens` / `num_heads`)
        # 执行DotProductAttention操作
        # 其实到这里才是自注意力的核心，我们将queries、keys、values都传进去，然后返回一个output
        # 在此之前只是通过将“多头”转移到batch_size这一维度上，这里才开始真正的自注意力
        # 这里的output的维度是(256,10,8)，第一维是256，第二维是10，第三维是32/4=8
        output = self.attention(queries, keys, values)

        # Shape of `output_concat`:
        # (`batch_size`, no. of queries, `num_hiddens`)
        # 这里相当于自注意力的“后处理”，将那些“多头”拼接回来，从而重新变成(64,10,32)
        output_concat = transpose_output(output, self.num_heads)

        # 这里的W_o是一个全连接层，将(64,10,32)变成(64,10,32)
        # 也就是说，这里的W_o是一个恒等映射，所以最终的输出就是(64,10,32)
        # 这里final_output就是我们MultiHeadAttention的最终输出

        return output_concat


class stanet(nn.Module):

    def __init__(self):
        super(stanet, self).__init__()

        # spatial attention
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=1, kernel_size=(cfg.decision_window, 1), stride=(1, 1))
        self.pooling1 = torch.nn.MaxPool2d(kernel_size=(3, 1), stride=(1, 1),padding=(1,0))
        self.linear1 = nn.Linear(cfg.elenum, 8)
        self.dropout = 0.5

        self.elu = nn.Sequential(
            nn.BatchNorm2d(num_features=1),
            nn.ELU(),
            nn.Dropout(p=self.dropout)
        )

        self.linear2 = nn.Linear(8, cfg.elenum)

        # conv block
        self.conv2 = nn.Conv2d(in_channels=cfg.elenum, out_channels=5, kernel_size=(1, 1), stride=(1, 1))
        self.pooling2 = torch.nn.MaxPool2d(kernel_size=(3, 1), stride=(4, 1),padding=(1,0))

        self.tanh = nn.Sequential(
            nn.BatchNorm2d(num_features=1),
            nn.Tanh(),
            nn.Dropout(p=self.dropout)
        )

        # 时间注意力
        self.attention = MultiHeadAttention(key_size=5, query_size=5,
                                            value_size=5, num_hiddens=5, num_heads=1, dropout=self.dropout)

        # 全连接
        self.fc1 = nn.Linear(5*cfg.decision_window//4, 4)

    def forward(self, E):
        E = E.unsqueeze(dim=1)

        # 空间注意
        R_c = self.conv1(E)
        R_s = self.pooling1(self.elu(R_c))
        M_s = self.linear2(self.elu(self.linear1(R_s)))

        # 利用广播机制，将M_s与E相乘
        Ep = M_s * E

        # 卷积块
        Ep = Ep.permute(0, 3, 2, 1)
        Epc = self.conv2(Ep)
        Epc = Epc.permute(0, 3, 2, 1)
        Eps = self.pooling2(self.tanh(Epc))

        # 时间注意
        Eps = Eps.squeeze(dim=1)
        E_t = self.attention(Eps, Eps, Eps)

        # 全连接
        E_t = E_t.reshape(E_t.shape[0], -1)
        final_out = self.fc1(E_t)

        return final_out




if __name__ == '__main__':
    # model = xanet()
    # print(model)
    # x2d = torch.randn(32, cfg.decision_window, 9, 9)
    # y = model(x2d)
    # model = CNN_baseline()
    # print(model)
    # x1d = torch.randn(32, cfg.decision_window, 59)
    # y = model(x1d)
    print(1)