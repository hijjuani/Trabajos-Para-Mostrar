import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("dark_background")

class StockAnalyzer:
    def __init__(self, ticker, period="34mo"):
        self.ticker = ticker
        self.period = period
        self.data = None
    
    def fetch_data(self):
        """Descarga los datos de la acción"""
        self.data = yf.download(self.ticker, period=self.period)
        return self.data
    
    def add_moving_averages(self, windows=[20, 50]):
        """Agrega medias móviles simples"""
        for w in windows:
            self.data[f"SMA{w}"] = self.data["Close"].rolling(w).mean()
    
    def plot_price_with_sma(self):
        """Grafica precio y medias móviles"""
        plt.figure(figsize=(12,6))
        plt.plot(self.data.index,
                 self.data["Close"],
                 label="Precio Cierre", 
                 color="white", 
                 linewidth=1.5)

        for col in self.data.columns:
            if "SMA" in col:
                plt.plot(self.data.index, self.data[col], label=col, linestyle="--", color = 'red')

        plt.title(f"Análisis de {self.ticker}", fontsize=16, color="white")
        plt.xlabel("Fecha", color="white")
        plt.ylabel("Precio (USD)", color="white")
        plt.legend()
        plt.grid(alpha=0.2)
        plt.show()


apple = StockAnalyzer("AAPL", period="34mo")
apple.fetch_data()
apple.add_moving_averages([20,50])
apple.plot_price_with_sma()


