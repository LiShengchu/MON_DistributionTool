# MON Distribution Tool

使用智能合约进行MON代币分发

## 功能特性
- 通过智能合约批量分发MON
- 支持自定义分发金额

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置账户
```
修改 config.yaml
设置RPC地址
添加主账户私钥
配置接收地址和金额

accounts:
  main:
    address: '主账户地址'
    private_key: '主账户私钥'
  recipients:
  - address: '分发地址1'
  - address: '分发地址2'
contractAddress: '部署后会自动生成'
distribute_amount: 0.05
network:
  rpc_url: https://testnet-rpc.monad.xyz/

```
3. 部署智能合约
```bash
python deploy.py
```

4. 执行分发
```bash
python distribute.py
```

## Support
- [Telegram](https://t.me/ligotg)
- [Twitter](https://x.com/liego16?s=21&t=EfHZN4xPR9a2T-OV-E3HVw)
