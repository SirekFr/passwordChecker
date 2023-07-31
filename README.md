# passwordChecker
## Checks if passwords input in arguments have been pwned at https://api.pwnedpasswords.com/range/
### Examples:
```
python passwordChecker.py test test2
```
>test was found 89159 times!
>
>test2 was found 2316 times!
>
>done!
```
python passwordChecker.py save test test2
python passwordChecker.py file
```
>checking saved passwords
>
>Password starting with te, has been leaked 89159 times.
>
>Password starting with te, has been leaked 2316 times.
>
```
python passwordChecker.py file mail sirek.frantisek@gmail.com
```
>checking saved passwords
>
>Mail sent

an email is sent to the inputted address with the regular output
```
python passwordChecker.py task sirek.frantisek@gmail.com 12:00
```
>Task created

a daily task is created in windows task scheduler that executes at 12:00 and checks saved passwords
and outputs to the inputted email address
