from machine import Pin, PWM
import time, network, socket, json

# ---------- WIFI ----------
ap = network.WLAN(network.AP_IF)
ap.active(True)
print("AP ACTIVE:", ap.active())
print("CONFIG:", ap.ifconfig())
ap.config(essid='RKIVE', password='RKIVE1234')
print("IP:", ap.ifconfig()[0])

# ---------- INPUTS ----------
dial = Pin(14, Pin.IN, Pin.PULL_UP)
ir = Pin(18, Pin.IN)

# ---------- OUTPUTS ----------
servo = PWM(Pin(25))
servo.freq(50)

def servo_open():
    servo.duty(120)
    time.sleep(1)

def servo_close():
    servo.duty(40)

green = Pin(19, Pin.OUT)
red = Pin(21, Pin.OUT)

# ---------- ROTARY ----------
last_state = 1
pulse_count = 0
last_time = 0

MIN_GAP = 150
MAX_GAP = 1000

COUNT_TIME = 5000
DIGIT_TIMEOUT = 1200

mode = "WAIT"
start_time = 0
locked = False


cooldown_until = 0
COOLDOWN = 3000


entered = ""
#correct = "11323115"
correct = "13214"
attempts = 3
status = "ENTER CODE"
stage = 1


current_morse = ""
letter_index = 0
correct_letters = ['...', '---', '...']



file_content = [
"INCIDENT REPORT: Time observed 1:32 AM",
"INTERVIEW: Seen thrice",
"RESIDENT FILE: Unit 1",
"ACCESS LOG: User ID 14",
"CALL LOGS: Irregular dialing",
"BUILDING NOTES: Distortion reported",
"FINAL FILE: LOCKED"
]


def page():
    return """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body{margin:0;background:#050505;color:#00ff9c;font-family:Courier New;overflow:hidden;}

.screen{
display:flex;justify-content:center;align-items:center;
height:100vh;flex-direction:column;text-align:center;
}

.wrap{
display:none;
height:100vh;
width:100%;
}

.side{width:260px;border-right:1px solid #00ff9c;overflow:auto;}
.file{padding:10px;border-bottom:1px dashed #033;cursor:pointer;}
.file:hover{background:#001;}
.locked{color:#033;cursor:not-allowed;}

.main{flex:1;padding:10px;white-space:pre-wrap;}

.locked.glitch{
animation:glitch 0.8s infinite;
color:#0a3322;
}

.box{
position:fixed;bottom:0;width:100%;
background:#000;padding:10px;border-top:1px solid #00ff9c;
display:none;
}

/* EFFECTS */
.flicker{animation:flicker 1.2s infinite;}
@keyframes flicker{0%{opacity:1;}50%{opacity:0.3;}100%{opacity:1;}}

.glitch{animation:glitch 1s infinite;}
@keyframes glitch{
0%{transform:translate(0);}
20%{transform:translate(-2px,1px);}
40%{transform:translate(2px,-1px);}
60%{transform:translate(-1px,1px);}
80%{transform:translate(1px,-1px);}
100%{transform:translate(0);}
}

button{
margin-top:20px;padding:10px;
background:black;border:1px solid #00ff9c;
color:#00ff9c;cursor:pointer;
}
button:hover{background:#001;}
</style>
</head>

<body>

<!-- SCREEN 1 -->
<div class="screen" id="start1">
<h2 class="flicker glitch">Are you ready to solve this mystery, DETECTIVE ELIAS?</h2>
<button onclick="next1()">BEGIN</button>
</div>

<!-- SCREEN 2 -->
<div class="screen" id="start2" style="display:none">
<h2 class="glitch">The archive has been restored.</h2>
<h3 class="flicker">But something is wrong.</h3>
<button onclick="showRules()">CONTINUE</button>
</div>

<!-- RULES -->
<div class="screen" id="rules" style="display:none">
<h3>1. Use the case files to solve Maya's murder.</h3>
<h3>2. Use the rotary phone to input the secret code.</h3>
<h3>3. You only have THREE attempts.</h3>
<h3 class="glitch">4. Don't forget, Elias.</h3>
<button onclick="startGame()">ENTER ARCHIVE</button>
</div>

<!-- GAME -->
<div class="wrap" id="game">
<div class="side" id="side"></div>
<div class="main" id="main">SELECT FILE</div>
</div>

<!-- PANEL -->
<div class="box" id="panel">
INPUT: <span id="live"></span><br>
STATUS: <span id="msg"></span><br>
MORSE: <span id="morse"></span><br>
ATTEMPTS: <span id="att"></span><br>
CODE LENGTH: <span id="length"></span><br>
COOLDOWN: <span id="cool"></span><br>
<button onclick="deleteDigit()">DELETE LAST DIGIT</button>
<button onclick="resetGame()">RESET GAME</button>
</div>

<script>

/* =========================================================
   🔥 EDIT YOUR FILE CONTENT HERE (THIS IS WHAT USER SEES)
   ========================================================= */

const FILE_DATA = [

`INCIDENT REPORT

METROPOLITAN POLICE DEPARTMENT
CASE ID: MQ-132
STATUS: ACTIVE
ASSIGNED TO: Detective Elias

---

Initial report filed following statement from victim regarding repeated sightings of an unidentified individual positioned outside her residence.

Subject described as remaining completely stationary during each sighting. No visible attempt at communication. No movement recorded.

No additional witnesses confirmed presence of subject at time of report.

---

Victim statement (excerpt):

“I checked more than once. The first time I thought I imagined it. The second time I thought it was someone waiting for someone else. The third time I knew it wasn’t normal.”

“It’s always the same time. Every night. It doesn’t change.”

“1:32 AM.”

---

Follow-up action was not initiated at the time of reporting due to lack of corroborating evidence and absence of immediate threat indicators.

No patrol unit dispatched.

Case remained open pending further escalation.

---

End of report.

---

>>> Time is very important in murder cases like this one. <<<`,

`INTERVIEW RECORD

INTERVIEW RECORD
FILE REFERENCE: INT-Ax

Subject: Mara Quinn
Interviewer: [REDACTED]

Interview conducted following escalation of initial report. Subject appeared fatigued, hesitant, and occasionally inconsistent in timeline recall.

Subject confirmed prior familiarity with the unidentified individual described in the incident report.

Transcript excerpt:

“I’ve seen him before. Not near my apartment. Somewhere else.”

“I didn’t think anything of it at the time. People look at people. That’s normal.”

“But it kept happening.”

“It wasn’t like he was following me directly. It was just… repetition.”

When asked about frequency of prior encounters:

“Three times that I can clearly remember.”

Subject showed visible discomfort when asked to describe the individual in detail. Description remained vague and non-specific.

No identifying characteristics provided.

End of file.

>>> Murderers often return to the scene of the crime. <<<`,

`RESIDENCE FILE

Name: Mara Quinn
Building: [REDACTED]
Floor: 1

Unit assignment confirmed through internal records and partial emergency call transcript recovery.

Building access logs show no irregular forced entry attempts within the relevant timeframe.

Neighbor reports indicate no audible disturbance prior to escalation event.

Emergency call transcript excerpt (reconstructed):

“He’s outside the door.”

“I can hear something.”

“I don’t know if he’s moving or if I just can’t hear it.”

“Third floor.”

“Unit 1.”

“I don’t think I locked it. I don’t remember if I locked it.”

No confirmed entry recorded.

No physical damage to door structure observed in post-incident inspection.

End of file.

>>> Where did the victim live? <<<`,

`ARCHIVE ACCESS LOG

System: Evidence Archive Terminal
Case Reference: MQ-XYZ

User Activity Detected During Active Investigation Window

User: ELIAS_V
Role: Evidence Analyst

Recovered fragments suggest intentional modification rather than system error.

Access Credential:

User ID: 14

Internal review flagged due to overlap between access activity and evidence inconsistency timeline.

No formal disciplinary action recorded.

End of log.

>>> Detectives don't usually access archives like this. <<<`,

`OUTGOING CALL LOGS

System extraction from building line history. Partial recovery due to signal degradation.

9:12 PM — 9821745631 — FAILED
9:18 PM — 221345671 — COMPLETED
9:23 PM — 563214331 — INTERRUPTED
9:31 PM — 331245671 — FAILED
9:37 PM — 221341562 — COMPLETED
9:42 PM — UNKNOWN — SIGNAL LOSS

Repeated attempts observed within a short time interval.

Sequence irregular. No consistent dialing pattern identified.

Interruptions occur mid-input in multiple instances.

No confirmed successful emergency connection logged within extracted dataset.

End of record.

>>> Call records are always important, right? <<<`,

`BUILDING OBSERVATION NOTES

---

Multiple residents reported inconsistencies in unit numbering across the third floor.

---

Lighting conditions within the corridor vary due to partial fixture failure.

Certain sections experience intermittent dimming.

Residents report that numbers on doors appear unclear or distorted under low light.

---

Maintenance inspections did not confirm structural faults.

No wiring issues detected that would explain reported acoustic anomalies.

---

Final note:

Reports considered subjective and not formally validated.

No corrective action taken.

Detective ELIAS recorded on scene.

---

End of notes.

>>> Some say the dead haunt where they used to be when revenge hasn't been taken for them. <<<`,

`ANSWERING MACHINE

FINAL INSTRUCTION

The system has identified abnormal signal interference.

Manual verification required.

Transmit identity using Morse protocol.

INPUT REQUIRED:

S O S

...

... --- ...

Failure to comply will result in permanent lockout.

>>> TRANSMIT SOS <<<`

];

/* ========================================================= */

var attempts = 3;

/* NAV */
function next1(){
start1.style.display="none";
start2.style.display="flex";
}

function deleteDigit(){
fetch("/delete").then(()=>{});
}

function showRules(){
start2.style.display="none";
rules.style.display="flex";
}

function startGame(){
rules.style.display="none";
game.style.display="flex";
panel.style.display="block";
renderFiles();
}

function resetGame(){
fetch("/reset").then(()=>{
location.reload();
});
}

/* OPEN FILE */
function openFile(i){
document.getElementById("main").innerText = FILE_DATA[i];
}

/* RENDER FILE LIST */
function renderFiles(){

let side=document.getElementById("side");
side.innerHTML="";

let names;

if(attempts>1){
names=[
"incident_report",
"interview_record",
"residence_file",
"access_log",
"call_logs",
"building_notes",
"answering_machine"
];
}else{
names=[
"TIME (1:32)",
"LOCKED",
"UNIT NUMBER (1)",
"USER ID (14)",
"LOCKED",
"LOCKED",
"LOCKED"
];
}

for(let i=0;i<names.length;i++){

let div=document.createElement("div");

/* NORMAL */
if(attempts>1){
div.className="file";
div.innerHTML=names[i];
div.onclick=()=>openFile(i);
}

/* LAST ATTEMPT */
else{

// ALLOW ONLY THESE FILES: 0, 2, 3
if(i==0 || i==2 || i==3){
div.className="file glitch";
div.innerHTML=names[i];
div.onclick=()=>openFile(i);
}

// LOCK EVERYTHING ELSE (INCLUDING INTERVIEW = i==1)
else{
div.className="file locked glitch";
div.innerHTML="FILES FLAGGED AS REDUNDANT<br><small>External Review Override</small>";
}
}

side.appendChild(div);
}
}

let lastCode = "";
let lockRender = false;

function updateUI(d){

document.getElementById("att").innerHTML = d.attempts_left_value;
document.getElementById("msg").innerHTML = d.status_message_text;

/* cooldown */
if(d.cooldown_active){
document.getElementById("cool").innerHTML = "WAIT 3s BEFORE NEXT INPUT";
}else{
document.getElementById("cool").innerHTML = "READY";
}

/* MORSE */
document.getElementById("morse").innerHTML =
d.morse_live_input_string + " | Letters: " + d.morse_progress_index;

document.getElementById("length").innerHTML = d.code_length_value;

attempts = d.attempts_left_value;

/* 🔥 FIX: force update even during rapid changes */
if(d.code_input_value !== lastCode){
lastCode = d.code_input_value;
document.getElementById("live").innerHTML = lastCode;

/* lock render for 1 cycle so last digit is not overwritten */
lockRender = true;
setTimeout(()=>{ lockRender=false; }, 50);
}else if(!lockRender){
document.getElementById("live").innerHTML = d.code_input_value;
}

renderFiles();
}

/* LIVE UPDATE LOOP */
setInterval(()=>{
fetch("/data")
.then(r=>r.json())
.then(d=>{
updateUI(d);
});
},200);

</script>

</body>
</html>
"""


addr = socket.getaddrinfo('0.0.0.0',80)[0][-1]
s=socket.socket()
s.bind(addr)
s.listen(1)
s.setblocking(False)


while True:

    try:
        conn,addr=s.accept()
        req=conn.recv(1024)

        if b"/data" in req:
            now = time.ticks_ms()
            remaining = 0

            if time.ticks_diff(cooldown_until, now) > 0:
                remaining = time.ticks_diff(cooldown_until, now) // 1000

            data=json.dumps({
                "code_input_value": entered,
                "status_message_text": status,
                "attempts_left_value": attempts,
                "game_stage_value": stage,
                "code_length_value": len(correct),
                "cooldown_seconds_value": remaining,
                "cooldown_active": time.ticks_diff(cooldown_until, now) > 0,
                "morse_live_input_string": current_morse,
                "morse_progress_index": letter_index,
                "morse_letters_done": letter_index
            })

            conn.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            conn.send(data)
            
        elif b"/reset" in req:
            entered = ""
            attempts = 3
            status = "ENTER CODE"
            stage = 1
            letter_index = 0
            current_morse = ""
            pulse_count = 0
            mode = "WAIT"
            locked = False
            servo_close()
            green.value(0)
            red.value(0)

            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nRESET")
            
        elif b"/delete" in req:
            if stage == 1:
                 if len(entered) > 0:
                     entered = entered[:-1]
                     status = "LAST DIGIT DELETED"
            elif stage == 2:
                if len(current_morse) > 0:
                    current_morse = current_morse[:-1]
                    status = "EDITING: " + current_morse  
            
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK")

        elif b"/file" in req:
            try:
                i=int(req.split(b"i=")[1].split(b" ")[0])
                msg=file_content[i]
            except:
                msg="ERROR"
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
            conn.send(msg)

        else:
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.send(page())

        conn.close()
    except:
        pass

   
    current = dial.value()
    now = time.ticks_ms()

    if time.ticks_diff(cooldown_until, now) > 0:
        last_state = current
        continue

    if mode == "WAIT":
        if last_state == 1 and current == 0:
            pulse_count = 1
            last_time = now
            start_time = now
            mode = "COUNT"
            locked = True

    elif mode == "COUNT":

        if not locked:
            if last_state == 1 and current == 0:
                gap = time.ticks_diff(now, last_time)

                if gap > MIN_GAP:
                    pulse_count += 1
                    last_time = now
                    locked = True

        if current == 1:
            locked = False

        if pulse_count > 0 and time.ticks_diff(now, last_time) > DIGIT_TIMEOUT:
            digit = pulse_count
            if digit == 10:
                digit = 0

            if len(entered) < len(correct):
                entered += str(digit)

            pulse_count = 0
            mode = "WAIT"
            cooldown_until = time.ticks_add(now,COOLDOWN)
        
           
        elif time.ticks_diff(now, start_time) > COUNT_TIME:
            digit = pulse_count
            if digit == 10:
                digit = 0
                
            if len(entered) < len(correct):
                entered += str(digit)
                status = "Enter next digit"

            pulse_count = 0
            mode = "WAIT"
            cooldown_until = time.ticks_add(now, COOLDOWN)
        last_state = current
        continue
   

    if len(entered) == len(correct) and stage == 1:
        if entered == correct:
            status = "ACCESS GRANTED"
            stage = 2
            entered = ""
        else:
            attempts -= 1
            status = "WRONG CODE"
            current_morse = ""
            entered = ""

    if stage == 2:
        if ir.value() == 0:
            start = time.ticks_ms()
            
            while ir.value() == 0:
                time.sleep_ms(1)

            duration = time.ticks_diff(time.ticks_ms(), start)

            if duration < 300:
                current_morse += '.'
            else:
                current_morse += '-'
                
            status = "INPUT: " + current_morse   

            green.value(1)
            time.sleep(0.1)
            green.value(0)

        else:
            start_gap = time.ticks_ms()
            while ir.value() == 1:
                time.sleep_ms(1)  

            gap = time.ticks_diff(time.ticks_ms(), start_gap)

            
            if gap > 1500 and current_morse != "":
                if letter_index < len(correct_letters) and current_morse == correct_letters[letter_index]:
                    letter_index += 1
                    status = "LETTER " + str(letter_index) + " CONFIRMED"   
                    
                else:
                    status = "WRONG MORSE"
                    red.value(1)
                    time.sleep(0.5)
                    red.value(0)
                    status = "WRONG LETTER - DELETE OR RETRY"   

                if letter_index == 3:
                    status = "IDENTITY CONFIRMED"
                    servo_open()
                    stage = 3

    time.sleep_ms(1)