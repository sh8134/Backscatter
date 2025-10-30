# Backscatter IoT Communication (Verilog + Python)

초저전력 IoT 센서를 위한 백스캐터 통신 시스템 구현 프로젝트입니다.  
Verilog로 동작하는 백스캐터 반사기(logic tag)와 Python 기반 GNURadio 소프트웨어를 통해  
저전력 무선 통신을 실험/개발합니다.

## 구성 요소

- **Verilog**: FPGA/ASIC 기반 백스캐터 송신기 (ASK/OOK 변조)
- **Python**: GNU Radio + ZMQ를 이용한 RF 신호 수신 및 디코딩
- **PlutoSDR**: 송수신 테스트 플랫폼

## 특징

- 20MHz 샘플링 기반의 실시간 진폭 기반 감지
- 초당 1비트 송신 (예: 센서 상태 전송)
- Complex-to-Mag + ZeroMQ 구조 기반 데이터 처리

## 실행 방법

1. `verilog/` 폴더: 백스캐터 송신기 논리 구성 (`.v` 파일)
2. `python/` 폴더: 수신기 및 분석 스크립트 (`rx_receiver.py` 등)
3. GNU Radio Flowgraph에서 ZMQ로 신호 수신 후, Python으로 비트 복원

## 주의사항

- Verilog 코드는 IGLOO Nano 기반으로 작성됨 (Libero SoC 사용)
- 수신 측은 PlutoSDR + GNU Radio 환경 필요

## 라이선스

MIT License
