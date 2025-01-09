import os
import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QTabWidget, QFileDialog, QScrollArea


class NetworkConfigApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('네트워크 설정')
        self.resize(400, 300)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_config_tab(), "설정")
        self.tabs.addTab(self.create_load_tab(), "불러오기")

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def create_config_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP 주소")
        layout.addWidget(QLabel("IP 주소:"))
        layout.addWidget(self.ip_input)

        self.subnet_input = QLineEdit()
        self.subnet_input.setPlaceholderText("서브넷 마스크")
        layout.addWidget(QLabel("서브넷 마스크:"))
        layout.addWidget(self.subnet_input)

        self.gateway_input = QLineEdit()
        self.gateway_input.setPlaceholderText("기본 게이트웨이")
        layout.addWidget(QLabel("기본 게이트웨이:"))
        layout.addWidget(self.gateway_input)

        self.dns1_input = QLineEdit()
        self.dns1_input.setPlaceholderText("기본 DNS")
        layout.addWidget(QLabel("기본 DNS:"))
        layout.addWidget(self.dns1_input)

        self.dns2_input = QLineEdit()
        self.dns2_input.setPlaceholderText("보조 DNS")
        layout.addWidget(QLabel("보조 DNS:"))
        layout.addWidget(self.dns2_input)

        apply_button = QPushButton('적용')
        apply_button.clicked.connect(self.apply_config)
        layout.addWidget(apply_button)

        save_button = QPushButton('설정 저장')
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)

        # 경로 안내 문구 추가
        path_info_label = QLabel("저장되는 경로를 수정하지 마세요. (프로그램 설치위치/config_files)")
        layout.addWidget(path_info_label)

        tab.setLayout(layout)
        return tab

    def create_load_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # 실행된 파일의 경로 가져오기
        current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 실행된 프로그램의 경로
        config_dir = os.path.join(current_dir, "config_files")

        # config_files 폴더가 없으면 생성
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # Scrollable area for saved configurations
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # 저장된 JSON 파일 버튼 생성
        json_files = [file for file in os.listdir(config_dir) if file.endswith('.json')]

        if not json_files:
            label = QLabel("저장된 설정 파일이 없습니다.")
            scroll_layout.addWidget(label)
        else:
            for file in json_files:
                btn = QPushButton(file)
                btn.clicked.connect(self.load_config)
                scroll_layout.addWidget(btn)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        tab.setLayout(layout)
        return tab

    def apply_config(self):
        ip = self.ip_input.text()
        subnet = self.subnet_input.text()
        gateway = self.gateway_input.text()
        dns1 = self.dns1_input.text()
        dns2 = self.dns2_input.text()

        try:
            os.system(f'netsh interface ip set address name="이더넷" static {ip} {subnet} {gateway}')
            os.system(f'netsh interface ip set dns name="이더넷" static {dns1}')
            os.system(f'netsh interface ip add dns name="이더넷" {dns2} index=2')
            QMessageBox.information(self, "완료", "네트워크 설정이 적용되었습니다!")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"네트워크 설정 중 오류가 발생했습니다: {e}")

    def save_config(self):
        # 실행된 파일의 경로 가져오기
        current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 실행된 프로그램의 경로
        config_dir = os.path.join(current_dir, "config_files")

        # config_files 폴더가 없으면 생성
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 저장 파일 경로 설정
        file_path, _ = QFileDialog.getSaveFileName(self, "설정을 저장할 파일 이름", config_dir, "JSON Files (*.json);;All Files (*)")

        if file_path:
            config = {
                "ip": self.ip_input.text(),
                "subnet": self.subnet_input.text(),
                "gateway": self.gateway_input.text(),
                "dns1": self.dns1_input.text(),
                "dns2": self.dns2_input.text()
            }
            try:
                with open(file_path, "w") as file:
                    json.dump(config, file)
                QMessageBox.information(self, "완료", "설정이 저장되었습니다!")

                # 불러오기 탭 갱신
                self.tabs.removeTab(1)  # 기존 탭 제거
                self.tabs.addTab(self.create_load_tab(), "불러오기")  # 새 탭 생성
            except Exception as e:
                QMessageBox.critical(self, "오류", f"설정을 저장하는 중 오류가 발생했습니다: {e}")

    def load_config(self):
        sender = self.sender()
        file_name = sender.text()

        # 실행된 파일의 경로 가져오기
        current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))  # 실행된 프로그램의 경로
        config_dir = os.path.join(current_dir, "config_files")
        file_path = os.path.join(config_dir, file_name)

        try:
            with open(file_path, "r") as file:
                config = json.load(file)
            self.ip_input.setText(config.get("ip", ""))
            self.subnet_input.setText(config.get("subnet", ""))
            self.gateway_input.setText(config.get("gateway", ""))
            self.dns1_input.setText(config.get("dns1", ""))
            self.dns2_input.setText(config.get("dns2", ""))
            QMessageBox.information(self, "완료", "설정이 불러와졌습니다!")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"설정을 불러오는 중 오류가 발생했습니다: {e}")


if __name__ == '__main__':
    app = QApplication([])
    window = NetworkConfigApp()
    window.show()
    app.exec_()
