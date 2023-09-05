# Retirado e adaptado de https://docs.sqlalchemy.org/en/20/orm/quickstart.html
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import requests
import statistics


class Base(DeclarativeBase):
    pass

class Temperaturator(Base):
    __tablename__ = "temperaturator"
    id: Mapped[int] = mapped_column(primary_key=True)
    local: Mapped[str] = mapped_column(String(30))
    description: Mapped[Optional[str]]
    endpoints: Mapped[List["EndPoint"]] = relationship(
        back_populates="temperaturator", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"Temperaturator(id={self.id!r}, local={self.local!r}, endpoints={len(self.endpoints)!r})"
    
    def media(self)-> float:
        lista = []
        for endp in self.endpoints:
            lista.append(endp.consume())
        return statistics.fmean(lista)
        
    
    

class EndPoint(Base):
    __tablename__ = "endpoint"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
    chaves: Mapped[List["Chave"]] = relationship(
        back_populates="endpoint", cascade="all, delete-orphan"
    )
    temperaturator_id: Mapped[int] = mapped_column(ForeignKey("temperaturator.id"))
    temperaturator: Mapped["Temperaturator"] = relationship(back_populates="endpoints")
    def __repr__(self) -> str:
        return f"EndPoint(id={self.id!r}, url={self.url!r})"
    
    def newChave(self, valor:str):
        novo = Chave()
        novo.endpoint = self
        novo.valor = valor
        novo.sequen = len(self.chaves)
        #self.chaves.append(novo)

    def consume(self) -> float:
        retorno = ""
        # TODO Tratar se aqui ele retornou algum erro
        resposta = requests.get(self.url).json()
        #Lembrar de explicar a gambiarra
        caminho = [x.valor for x in self.chaves]
        retorno = float(deep_get(resposta,caminho))
        return retorno

class Chave(Base):
    __tablename__ = "chaves"
    id: Mapped[int] = mapped_column(primary_key=True)
    sequen: Mapped[int]
    valor: Mapped[str]
    endpoint_id: Mapped[int] = mapped_column(ForeignKey("endpoint.id"))
    endpoint: Mapped["EndPoint"] = relationship(back_populates="chaves")
    def __repr__(self) -> str:
        return f"{self.valor!r}" 
        #return f"Chave(id={self.id!r}, sequencia={self.sequen!r}, valor={self.valor!r})"

def deep_get(d, keys):
    '''
    from: https://stackoverflow.com/questions/25833613/safe-method-to-get-value-of-nested-dictionary
    '''
    if not keys or d is None:
        return d
    return deep_get(d.get(keys[0]), keys[1:])
    

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/postgres')

Base.metadata.create_all(engine)
persistencia = Session(engine)

'''
from Model import *
t = Temperaturator()
t.local = 'Natal'
t.description = 'Minha cidade'
persistencia.add(t)
persistencia.commit()
e = EndPoint()
e.url = 'https://api.open-meteo.com/v1/forecast?latitude=-5.795&longitude=-35.2094&current_weather=true'
e.newChave('current_weather')
e.newChave('temperature')
e.temperaturator = t
persistencia.add(e)
novo = EndPoint()
novo.url = 'https://api.openweathermap.org/data/2.5/weather?lat=-5.79&lon=-35.21&units=metric&appid=3489c35b15d5becad35f4461edd7c361'
novo.temperaturator = t
novo.newChave('main')
novo.newChave('temp')
persistencia.add(novo)
outro = EndPoint()
outro.url = 'http://api.weatherapi.com/v1/current.json?key=4169d18cdef84c8ab49140853230309&q=natal&aqi=no'
outro.newChave('current')
outro.newChave('temp_c')
outro.temperaturator = t
persistencia.add(outro)
persistencia.commit()
'''