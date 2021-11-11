#!/usr/bin/env python
# CHORUS!!!
import time
from common import *
from music_content import *

  
def play(pwm_array, ctnt):
    beats = ctnt.get('beats', 120)
    one = 60.0 / beats
    print('> START')

    a_right = time_list(ctnt.get('right', ()))
    a_left = time_list(ctnt.get('left', ()))
    a_chore = time_list(ctnt.get('chore', ()))
    a_chore2 = time_list(ctnt.get('chore2', ()))
    amix:list = []
    amix.extend(a_right)
    amix.extend(a_left)
    amix.extend(a_chore)
    amix.extend(a_chore2)
    amix = sort_timeline(amix)
    amix = decorate_timeline(amix)  
    act_line = get_action_list(amix)
#     print('ACT LINE:')
#     for x in act_line:
#         print(x)
 
    print('===START=======')
    print('# MUSIC NAME: {}'.format(ctnt['name']))
    print('# BEATS: {}\tONE: {}'.format(str(beats), str(one)))
    print('')
             
    print('> RESET')
    reset(pwm_array) 
    for x in act_line:
        print('> TIME:\t{}'.format(str(x['time'])))
        for note_item in x['notes']:
            ntime, note, ndrt, nspan = note_item
            channel, pwm_idx, srv_idx = servo_table.get(note)
            ang = f_angle(note)
            span_t = x['span'] * one
            
            print('> SERV   {}:\t{}\t{}\t{}'.format(str(note), str(x['span']), str(channel), ndrt))
            if channel != -1: # NOT note_0
                if ndrt == 'DOWN':
                    set_servo_angle(pwm_array[pwm_idx], srv_idx, ang)
                else: # 'UP'
                    set_servo_angle(pwm_array[pwm_idx], srv_idx, 0)
            
        time.sleep(span_t)
        pass
    
    print('===END======')
    time.sleep(.5)
    reset(pwm_array)
    print('> END')


if __name__=='__main__':
    pwm_array = init_pwm()
    last = 0
    while True:
        idx = 0
        print('SELECT music: (0 for test; -1 to exit.)')
        for i in range(len(music_content)):
            print('{}. {}'.format(str(i+1), music_content[i]['name']))
        ctnt = input()
        if ctnt == 'r' or ctnt == '':
            idx = last
        else:
            idx = int(ctnt)
            last = idx
        if idx < 0:
            print('BYE~')
            break
        if idx == 0:
            print('TEST')
            ctnt = music_test
            play(pwm_array, ctnt)
        else:
            idx = idx - 1
            ctnt = music_content[idx]
            play(pwm_array, ctnt)
          
