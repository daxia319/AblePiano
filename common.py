import time
import math

import Adafruit_PCA9685
from functools import cmp_to_key


'''
(Channel, PWM, ID_of_PWM)
'''
servo_table = {
    '0'  : (-1, -1, -1),
    # WHITE
    '1--': (0, 0, 0),   '2--': (1, 0, 1),   '3--': (2, 0, 2),
    '4--': (3, 0, 3),   '5--': (4, 0, 4),   '6--': (5, 0, 5),   '7--': (6, 0, 6),
    '1-' : (7, 0, 7),   '2-' : (8, 0, 8),   '3-' : (9, 0, 9),
    '4-' : (10, 0, 10), '5-' : (11, 0, 11), '6-' : (12, 0, 12), '7-' : (13, 0, 13),
    '1'  : (14, 0, 14), '2'  : (15, 0, 15),
    
    '3'  : (16, 1, 0),  '4'  : (17, 1, 1),  '5'  : (18, 1, 2),
    '6'  : (19, 1, 3),  '7'  : (20, 1, 4),
    '1+' : (21, 1, 5),  '2+' : (22, 1, 6),  '3+' : (23, 1, 7),  '4+' : (24, 1, 8),
    '5+' : (25, 1, 9),  '6+' : (26, 1, 10), '7+' : (27, 1, 11),
    '1++': (28, 1, 12), '2++': (29, 1, 13), '3++': (30, 1, 14), '4++': (31, 1, 15),
    
    '5++': (32, 2, 9),  '6++': (33, 2, 10),  '7++': (34, 2, 11),
    '1+++':(35, 2, 12),   
    
    # BLACK
    '#1--': (100, 3, 0), '#2--': (101, 3, 1), '#4--': (102, 3, 2),
    '#5--': (103, 3, 3), '#6--': (104, 3, 4),
    '#1-' : (105, 3, 5), '#2-' : (106, 3, 6), '#4-' : (107, 3, 7),
    '#5-' : (108, 3, 8), '#6-' : (109, 3, 9),
    '#1'  : (110, 3, 10),'#2'  : (111, 3, 11),'#4'  : (112, 3, 12),
    '#5'  : (113, 3, 13),'#6'  : (114, 3, 14),
    '#1+' : (115, 3, 15),
    
    '#2+' : (116, 2, 0), '#4+' : (117, 2, 1), '#5+' : (118, 2, 2), '#6+' : (119, 2, 3),
    '#1++': (120, 2, 4), '#2++': (121, 2, 5), '#4++': (122, 2, 6),
    '#5++': (123, 2, 7), '#6++': (124, 2, 8),
    
}

LIT_SPAN = 0.01

ANGLE_BLACK = 50
ANGLE_WHITE = 52
angle_table = {
    '6--': 55,
    '1-':  55,
    '3-':  55,
    '7-':  53,
    '5':   55,
    '4+':  55,
    '3++': 55,
    '6++': 55,
    '1+++': 55,
    '#1--': 55,
    '#2--': 55,
    '#4--': 40,
    '#1':  50,
    '#2':  50,
    '#4':  55,
    '#1+': 50,
    '#2+': 50,
    }
#angle_table = {}
 

def init_pwm():
    # Total 61 notes
    pwm1 = Adafruit_PCA9685.PCA9685(address=0x41) #[1--, 2], 16 notes
    pwm2 = Adafruit_PCA9685.PCA9685(address=0x42) #[3, 4++], 16 notes
    pwm4 = Adafruit_PCA9685.PCA9685(address=0x44) #[1+, #6++] OR [5++, 1+++], 9+4=13 notes
    pwm5 = Adafruit_PCA9685.PCA9685(address=0x45) #[1--, #1+], 16 notes

    pwm_array=[pwm5, pwm4, pwm2, pwm1]
    for pwm in pwm_array:
        pwm.set_pwm_freq(50)
    
    return pwm_array
    
    
def set_servo_angle(pwm0, channel, angle):
    date=int(4096*((angle*11)+500)/(20000)+0.5)
    pwm0.set_pwm(channel, 0, date)
    

'''
return: (note, span)
'''
def f_note(note):
    #print(note) ###DEBUG
    alist = note.split('^')
    if len(alist) == 1:
        anote = note
        aspan = 1.0
    elif len(alist) > 2:
        print('Error: wrong note format.')
        print(note)
        exit(-2)
    else:
        anote, span = alist[:2]
        if span == '=':
            aspan = .25
        elif span == '-':
            aspan = .5
        else:
            print(note)
            aspan = float(span)        
    return (anote, aspan)
    
    
# def f_channel(channel):
#     if channel < 100: # white
#         pwm_idx = channel // 16
#         srv_idx = channel % 16
#     else: # black
#         ac = channel-100
#         pwm_idx = 3 + ac // 16
#         srv_idx = ac % 16
#     return (pwm_idx, srv_idx)


def f_angle(note):
    if note.startswith('#'): #BLACK
        angle = angle_table.get(note, ANGLE_BLACK)
    else:                     #WHITE
        angle = angle_table.get(note, ANGLE_WHITE)        
            
    return angle


def reset(pwm_array):
    for pwm in pwm_array:
        for i in range(16):
            set_servo_angle(pwm, i, 0)
        time.sleep(0.5)
        

def time_list(note_list):
    timeline = 0.0
    ret = []
    for note in note_list:
        #print(note)
        anote, span = f_note(note)        
        if span < 0:
            print('timelist ERR')
            print(note)
            exit(2)
        ret.append([timeline, anote, 'DOWN', span])
        timeline += span
        ret.append([timeline, anote, 'UP', span])      
    return ret


def cmp_time_item(x, y):
    if x[0] > y[0]:
        return 1
    elif x[0] < y[0]:
        return -1
    else:
        if x[2] == 'UP' and y[2] == 'DOWN':
            return -1
        elif x[2] == 'DOWN' and y[2] == 'UP':
            return 1
        else:
            return 0


def sort_timeline(atime_list):
    return sorted(atime_list, key=cmp_to_key(cmp_time_item))


def decorate_timeline(atime_list):
    for i in range(len(atime_list)):
        cur = atime_list[i]
        ctime, note, drt, span = cur
        nxt_time = ctime
        if drt != 'UP':
            continue
        if note == '0':
            continue
        for j in range(i+1, len(atime_list)):
            nxt = atime_list[j]
            #(ntime, nnote, ndrt, nspan)            
            ntime, nnote, ndrt = nxt[:3]            
            if ndrt == 'DOWN' and nnote == note:
                if math.fabs(ntime - nxt_time) < 1e-6:
                    cur[0] -= max(LIT_SPAN, span/8)
                
    return atime_list


def get_action_list(atime_list):
    ret:dict = {}
    for x in atime_list:
        #(time, note, drt, span)
        atime = x[0]
        if ret.get(atime) is None:
            ret[atime] = [x]
        else:
            ret[atime].append(x)

    time_line = []
    for k, v in ret.items():
        item = {'time':  k, 'notes': v, 'span': 0}
        time_line.append(item)
       
    time_line = sorted(time_line, key=lambda x:x['time'])
    last = None
    for item in time_line:
        if last is not None:
            aspan = item['time'] - last['time']
            if aspan >= 0:
                last['span'] = aspan
            else:
                print('ERROR')
                print(item)
                print(last['time'])
                exit(-1)
        last = item

    return time_line

