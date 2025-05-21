import sys
import os
import threading
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                           QTextEdit, QLabel, QComboBox, QProgressBar, QVBoxLayout,
                           QHBoxLayout, QWidget, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Biblioteca Groq não encontrada. Instale com: pip install groq")

class TranscriptionThread(QThread):
    """Thread para processamento de transcrição"""
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, filename, language="pt", model="whisper-large-v3-turbo"):
        super().__init__()
        self.filename = filename
        self.language = language
        self.model = model
        
    def run(self):
        if not GROQ_AVAILABLE:
            self.error_signal.emit("Biblioteca Groq não está instalada")
            return
            
        try:
            self.update_signal.emit("Inicializando...")
            
            # Inicializa cliente Groq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                self.error_signal.emit("Chave API Groq não encontrada no arquivo .env")
                return
                
            client = Groq(api_key=api_key)
            
            self.update_signal.emit("Enviando arquivo para transcrição...")
            
            # Abre o arquivo de áudio
            with open(self.filename, "rb") as file:
                # Cria uma transcrição do arquivo de áudio
                transcription = client.audio.transcriptions.create(
                    file=(self.filename, file.read()),
                    model=self.model,
                    prompt="Transcreva o audio com alta precisão",
                    response_format="verbose_json",
                    language=self.language,
                    temperature=0.0
                )
                
                # Envia o resultado
                self.finished_signal.emit(transcription.text)
                    
        except Exception as e:
            self.error_signal.emit(f"Erro na transcrição: {str(e)}")

class AudioTranscriberApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transcritor de Áudio")
        self.setMinimumSize(800, 500)
        self.audio_filename = ""
        self.transcription_thread = None
        
        # Inicializar a interface
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        # Criar widget central
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Cabeçalho
        header = QLabel("Transcritor de Áudio")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Área de configuração
        config_layout = QHBoxLayout()
        
        # Seleção de idioma
        language_label = QLabel("Idioma:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Português (pt)", "English (en)", "Español (es)", "Français (fr)"])
        config_layout.addWidget(language_label)
        config_layout.addWidget(self.language_combo)
        
        # Seleção de modelo
        model_label = QLabel("Modelo:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["whisper-large-v3-turbo", "whisper-large-v3"])
        config_layout.addWidget(model_label)
        config_layout.addWidget(self.model_combo)
        
        main_layout.addLayout(config_layout)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.select_file_btn = QPushButton("Selecionar Arquivo de Áudio")
        self.select_file_btn.setMinimumHeight(40)
        self.select_file_btn.clicked.connect(self.select_audio_file)
        button_layout.addWidget(self.select_file_btn)
        
        self.transcribe_btn = QPushButton("Transcrever")
        self.transcribe_btn.setMinimumHeight(40)
        self.transcribe_btn.clicked.connect(self.start_transcription)
        self.transcribe_btn.setEnabled(False)
        self.transcribe_btn.setStyleSheet("background-color: #6aa84f; color: white; font-weight: bold;")
        button_layout.addWidget(self.transcribe_btn)
        
        main_layout.addLayout(button_layout)
        
        # Status e barra de progresso
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Pronto")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        main_layout.addLayout(status_layout)
        
        # Área de resultados
        self.file_info_label = QLabel("Nenhum arquivo selecionado")
        main_layout.addWidget(self.file_info_label)
        
        self.transcription_text = QTextEdit()
        self.transcription_text.setReadOnly(False)  # Permite edição
        self.transcription_text.setPlaceholderText("A transcrição aparecerá aqui...")
        main_layout.addWidget(self.transcription_text, 1)  # Expansão vertical
        
        # Botões de exportação
        export_layout = QHBoxLayout()
        self.export_txt_btn = QPushButton("Exportar para TXT")
        self.export_txt_btn.clicked.connect(self.export_to_txt)
        
        self.copy_btn = QPushButton("Copiar para Área de Transferência")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        
        export_layout.addWidget(self.export_txt_btn)
        export_layout.addWidget(self.copy_btn)
        main_layout.addLayout(export_layout)
        
        # Definir o widget central
        self.setCentralWidget(central_widget)
    
    def select_audio_file(self):
        """Abre diálogo para selecionar arquivo de áudio"""
        file_filter = "Arquivos de Áudio (*.mp3 *.wav *.ogg *.flac);;Todos os Arquivos (*)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Áudio", "", file_filter)
        
        if file_path:
            self.audio_filename = file_path
            self.file_info_label.setText(f"Arquivo: {os.path.basename(file_path)}")
            self.transcribe_btn.setEnabled(True)
    
    def start_transcription(self):
        """Inicia o processo de transcrição"""
        if not self.audio_filename:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo de áudio primeiro.")
            return
        
        # Extrair código de idioma do texto do combobox
        language_text = self.language_combo.currentText()
        language_code = language_text.split("(")[1].split(")")[0]
        
        # Obter modelo selecionado
        model = self.model_combo.currentText()
        
        # Iniciar thread de transcrição
        self.transcription_thread = TranscriptionThread(self.audio_filename, language_code, model)
        self.transcription_thread.update_signal.connect(self.update_status)
        self.transcription_thread.finished_signal.connect(self.transcription_complete)
        self.transcription_thread.error_signal.connect(self.show_error)
        
        # Atualizar interface
        self.progress_bar.setVisible(True)
        self.status_label.setText("Transcrevendo...")
        self.transcribe_btn.setEnabled(False)
        self.select_file_btn.setEnabled(False)
        
        # Iniciar thread
        self.transcription_thread.start()
    
    def update_status(self, message):
        """Atualiza o status da transcrição"""
        self.status_label.setText(message)
    
    def transcription_complete(self, text):
        """Callback quando a transcrição for concluída"""
        self.transcription_text.setText(text)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Transcrição concluída!")
        self.transcribe_btn.setEnabled(True)
        self.select_file_btn.setEnabled(True)
    
    def show_error(self, error_message):
        """Exibe mensagem de erro"""
        QMessageBox.critical(self, "Erro", error_message)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Erro na transcrição")
        self.transcribe_btn.setEnabled(True)
        self.select_file_btn.setEnabled(True)
    
    def export_to_txt(self):
        """Exporta a transcrição para um arquivo TXT"""
        if not self.transcription_text.toPlainText().strip():
            QMessageBox.warning(self, "Aviso", "Não há texto para exportar.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Transcrição", "", "Arquivos de Texto (*.txt)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.transcription_text.toPlainText())
                QMessageBox.information(self, "Sucesso", f"Transcrição salva em {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo: {str(e)}")
    
    def copy_to_clipboard(self):
        """Copia a transcrição para a área de transferência"""
        if not self.transcription_text.toPlainText().strip():
            QMessageBox.warning(self, "Aviso", "Não há texto para copiar.")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.transcription_text.toPlainText())
        self.status_label.setText("Texto copiado para a área de transferência!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Configurar estilo global
    app.setStyle("Fusion")
    
    # Criar e mostrar a janela principal
    window = AudioTranscriberApp()
    window.show()
    
    sys.exit(app.exec_())