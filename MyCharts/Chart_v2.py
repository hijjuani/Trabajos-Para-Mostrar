import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import LogFormatter

class GráficoBase:

    def __init__(self, ticker, period='2y', sma_period=[], ema_period = [], rsi_period = 14, scale = 'linear'):

        # Configuración estética del gráfico
        self.ticker = ticker
        self.period = period
        self.sma_period = sma_period
        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.scale = scale
        self.pad = 15

        # Descargar los datos de Yahoo Finance
        self.data = yf.download(self.ticker, period=self.period)
        
        # Crear el gráfico
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 7), sharex=False, gridspec_kw={'height_ratios': [10, 2]})

        # Paleta de colores oscuros y fríos
        self.colors = {
            'line': '#FF1493',      
            'background': "#141823",
            'background_2': "#131A2C",
            'grid': "#33323245",
            'highlight': '#00BFFF'  
        }
        
        # Fuentes modernas y minimalistas
        self.fonts = {
            'title': {'family': 'Arial', 'weight': 'bold', 'size': 18, 'color':'w'},
            'labels': {'family': 'Arial', 'weight': 'regular', 'size': 12, 'color':'w'},
            'ticks': {'family': 'Arial', 'weight': 'regular', 'size': 10, 'labelcolor':'w'}
        }
        

        self.create_plot(fig, ax1, ax2)
        

    def create_plot(self, fig, ax, ax_rsi):
        
        # Fondo
        fig.patch.set_facecolor(self.colors['background'])
        ax.set_facecolor(self.colors['background_2'])
        
        # Graficar el precio de cierre con color violeta oscuro
        ax.plot(self.data.index, self.data['Close'], label=f'{self.ticker}', color=self.colors['line'], linewidth=1.4)
        
        # Cuadrícula
        ax.grid(True, color=self.colors['grid'], linestyle='-', linewidth=0.4)
        
        # Fechas (eje X)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %Y'))
        plt.xticks(rotation=45)
        
        # Título y etiquetas con el estilo personalizado
        ax.set_title(f'{self.ticker}', **self.fonts['title'], pad = self.pad)
        ax.set_xlabel('Date', **self.fonts['labels'], labelpad = self.pad)
        ax.set_ylabel('Price (USD)', **self.fonts['labels'], labelpad = self.pad)

        # Configuración de los ticks  
        ax.tick_params(axis='both', 
                       labelsize=self.fonts['ticks']['size'], 
                       labelcolor=self.fonts['ticks']['labelcolor'],
                       which = 'both')  # which hace que afecte a todos los ticks cuando uso la escala logarítmica

        # Escala
        ax.set_yscale(self.scale)
        if self.scale == 'log':
            """ Si quiero cambiar los ticks en logaritmo """
            ax.yaxis.set_major_formatter(LogFormatter())   
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4))  

        # Graficar SMA
        if self.sma_period:
            self.sma(ax)
        # Grafica EMA
        if self.ema_period:
            self.ema(ax)

        # Grafica RSI
        self.rsi(ax_rsi)

        # Leyenda
        ax.legend(facecolor=self.colors['background'], 
                  loc='upper left', 
                  fontsize=10, 
                  frameon=False, 
                  labelcolor='white')
        
        # Marca de agua
        fig.text(0.98, 0.89, "Juani © 2025",
         ha='right', va='bottom',
         fontsize=10, color='gray', alpha=0.8)

        # Mostrar el gráfico
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.3)
        plt.show()


    def sma(self, ax):


        for p in self.sma_period:
            # Calcular la media móvil (SMA)
            self.data[f'SMA{p}'] = self.data['Close'].rolling(p).mean()

            # Graficar la media móvil de 200 días con color rojo brillante (resaltado)
            ax.plot(self.data.index, 
                   self.data[f'SMA{p}'], 
                   label=f'SMA {p}', 
                   #color=self.colors['sma'], 
                   linestyle=':', 
                   linewidth=0.8)
            
    def ema(self, ax):
        for p in self.ema_period:
            col = f'EMA{p}'
            # adjust=False usa la fórmula recursiva típica de trading (pondera más lo reciente)
            self.data[col] = self.data['Close'].ewm(span=p, adjust=False).mean()
            ax.plot(self.data.index, 
                    self.data[col],
                    label=f'EMA {p}', 
                    linestyle='-.', 
                    linewidth=0.8, 
                    alpha=0.95)

    def rsi(self, ax2):
        delta = self.data['Close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self.data['RSI'] = rsi

        ax2.set_facecolor(self.colors['background_2'])
        ax2.plot(self.data.index, self.data['RSI'], color=self.colors['highlight'], label='RSI', linewidth = 0.7)
        ax2.tick_params(axis='x', labelbottom=False, labelcolor = self.fonts['ticks']['labelcolor'])
        ax2.tick_params(axis='y', labelcolor = self.fonts['ticks']['labelcolor'])
        ax2.axhline(70, color='red', linestyle='-', linewidth = 0.3)
        ax2.axhline(30, color='green', linestyle='-', linewidth = 0.3)
        ax2.set_ylabel('RSI', color = self.fonts['labels']['color'], labelpad = self.pad)

        plt.tight_layout()


# GráficoBase(ticker = '', period = '', sma_period = [], ema_period = [], scale = 'linear')

plot = GráficoBase(ticker='VIST', period='3y', sma_period=[50, 100], ema_period=[20, 200], scale='linear')