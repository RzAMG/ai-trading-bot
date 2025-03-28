from hashem import *



def SmartTP(position , timeframe ): 

    position_lot = position._asdict()['volume']
    position_symbol = position._asdict()['symbol']
    buy_price = mt5.symbol_info_tick(position_symbol).ask
    p_rsi = rsi(timeframe , position_symbol)
    if position._asdict()['type'] == 1 :
        #short position
        if p_rsi < 30  :
            ticket = position._asdict()['ticket']
            close_order(position_symbol , position_lot , buy , buy_price , ticket)


    sell_price = mt5.symbol_info_tick(position_symbol).bid
    if position._asdict()['type'] == 0 :
        #long position
        if p_rsi > 70:
            ticket = position._asdict()['ticket']
            close_order(position_symbol , position_lot , sell , sell_price , ticket) 
           




def verify_not_range(symbol):

    uper = nadaraya(symbol, '1m', mult=3, h=4.0 , updown='up')
    down = nadaraya(symbol, '1m', mult=3, h=4.0 , updown='down')
    Avrage18 = Avrage(symbol ,'1m',18)
    if Avrage18[-1] < uper[-1] and Avrage18[-1] > down[-1] and Avrage18[-3] < uper[-3] and Avrage18[-3] > down[-3]   and Avrage18[-6] < uper[-6] and Avrage18[-6] > down[-6] :
        return False
    else:
        return True



def modify_profit(position , Position_price):
    #long
    if position._asdict()['type'] == 0 :

        more_profit =  ((Position_price -  position._asdict()['price_open'])/3)

        if position._asdict()['price_open'] + more_profit > position._asdict()['sl']:
            modify_position(position._asdict()['ticket'] , (position._asdict()['price_open'] + more_profit ))
    else:
        more_profit =  (( position._asdict()['price_open'] - Position_price )/3)

        if position._asdict()['price_open'] - more_profit < position._asdict()['sl']:
            modify_position(position._asdict()['ticket'] , (position._asdict()['price_open'] - more_profit ))

