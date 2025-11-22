# Pydroid 3 Math Solver
"""
To'liq matematik yechuvchi (Pydroid 3 versiyasi).
Qo'llab-quvvatlanadigan buyruqlar:
- oddiy ifodalar: 2+3*4, (5+3)/2, 2^5
- tenglama: x^2-4=0
- integral: integral x^2 dx
- hosila: diff(x**3) yoki d/dx x^3
- limit: limit(sin(x)/x, x, 0)
- plot x^2 (grafik chizish)
- exit (chiqish)
"""

import sys
import math

# Sympy kutubxonasini chaqirish
try:
    from sympy import (
        symbols, sympify, simplify, factor, expand, solveset, S,
        integrate, diff, limit, Eq
    )
    from sympy.parsing.sympy_parser import (
        parse_expr, standard_transformations, implicit_multiplication_application
    )
    from sympy.plotting import plot
except ImportError:
    print("XATO: 'sympy' kutubxonasi o'rnatilmagan!")
    print("Iltimos, Pydroid menyusidan 'Pip' ga kirib 'sympy' va 'matplotlib' ni o'rnating.")
    sys.exit()

# O'zgaruvchilarni ko'paytirishni to'g'irlash (2x -> 2*x)
transformations = standard_transformations + (implicit_multiplication_application,)

# Global o'zgaruvchi
x = symbols('x')

def normalize(s: str) -> str:
    """Belgilarni Python tushunadigan holatga keltiradi"""
    s = s.replace('^', '**')
    s = s.replace('×', '*')
    s = s.replace('÷', '/')
    s = s.replace(':', '/')
    s = s.replace('√', 'sqrt')
    # G'alati tire belgilarini to'g'irlash
    s = s.replace('—', '-').replace('–', '-')
    return s.strip()

def try_parse(expr: str):
    """Ifodani sympy obyektiga aylantirish"""
    expr = normalize(expr)
    return parse_expr(expr, transformations=transformations)

def handle_equation(text: str):
    """Tenglamani yechish"""
    try:
        left, right = text.split('=', 1)
        L = try_parse(left)
        R = try_parse(right)
        
        # O'zgaruvchilarni aniqlash
        eq = Eq(L, R)
        vars_ = list(L.free_symbols.union(R.free_symbols))
        
        if not vars_:
            return f"Tenglama: {left} = {right}\nNatija: {'To\'g\'ri' if L.equals(R) else 'Noto\'g\'ri'}"
        
        var = vars_[0] # Birinchi topilgan o'zgaruvchini olamiz
        sol = solveset(eq, var, domain=S.Complexes)
        return f"Tenglama: {left} = {right}\nO'zgaruvchi: {var}\nYechim: {sol}"
    except Exception as e:
        return f"Tenglamada xato: {e}"

def handle_integral(text: str):
    try:
        t = text.lower().replace('integral', '').replace('integrate', '').replace('∫', '').strip()
        # "dx" ni olib tashlash
        if t.endswith('dx'):
            t = t[:-2].strip()
        
        f = try_parse(t)
        var = list(f.free_symbols)[0] if f.free_symbols else x
        res = integrate(f, var)
        return f"∫ ({f}) d{var} = {res} + C"
    except Exception as e:
        return f"Integral xatosi: {e}"

def handle_derivative(text: str):
    try:
        t = text.lower()
        # "d/dx" yoki "diff" so'zlarini tozalash
        if t.startswith('d/d'):
            parts = text.split(None, 1)
            if len(parts) > 1:
                t = parts[1]
        t = t.replace('derivative', '').replace('diff', '').strip()
        
        f = try_parse(t)
        var = list(f.free_symbols)[0] if f.free_symbols else x
        res = diff(f, var)
        return f"d/d{var} ({f}) = {res}"
    except Exception as e:
        return f"Hosila xatosi: {e}"

def handle_limit(text: str):
    try:
        # Format: limit(sin(x)/x, x, 0)
        obj = try_parse(text)
        res = obj.doit()
        return f"Limit natijasi: {res}"
    except:
        # Agar oddiy matn kiritilsa (parsing qiyin bo'lsa)
        return "Limit formati xato. To'g'ri format: limit(sin(x)/x, x, 0)"

def handle_plot(text: str):
    """Grafik chizish"""
    try:
        expr_str = text[4:].strip() # "plot " so'zini olib tashlash
        sym = try_parse(expr_str)
        print(f"Grafik chizilmoqda: {sym} ...")
        # Pydroid uchun show=True muhim, lekin odatda avtomatik ishlaydi
        plot(sym, show=True)
        return "Grafik yakunlandi."
    except ImportError:
        return "XATO: Grafik chizish uchun 'matplotlib' kutubxonasini o'rnating (Pip orqali)."
    except Exception as e:
        return f"Grafik xatosi: {e}"

def handle_other(expr_text: str):
    """Soddalashtirish va hisoblash"""
    try:
        s_norm = normalize(expr_text)
        low = s_norm.lower()
        
        # Maxsus buyruqlar
        if low.startswith(('factor', 'expand', 'simplify')):
            res = try_parse(s_norm)
            return f"Natija: {res}"

        # Oddiy ifoda
        f = try_parse(s_norm)
        out = f"Ifoda: {f}\n"
        
        # Sonli qiymat (agar mumkin bo'lsa)
        try:
            numeric = f.evalf()
            out += f"Taqribiy qiymat: {numeric}\n"
        except:
            pass
            
        out += f"Soddalashtirilgan: {simplify(f)}"
        return out
    except Exception as e:
        return f"Xato: {e}"

def show_help():
    print("""
--- QO'LLANMA ---
1. Hisoblash: 2+2, 5^2, sqrt(16)
2. Tenglama: x^2 - 9 = 0
3. Integral: integral x^2
4. Hosila: diff(x^3) yoki d/dx sin(x)
5. Limit: limit(sin(x)/x, x, 0)
6. Grafik: plot x^2
7. Chiqish: exit
-----------------
""")

def main():
    print("=== Pydroid Matematik Yechuvchi ===")
    print("Buyruqni kiritib Enter bosing (Yordam uchun: help)")
    
    while True:
        try:
            text = input("\n>>> ").strip()
            if not text:
                continue
                
            low = text.lower()
            
            if low in ['exit', 'quit']:
                print("Dastur tugatildi.")
                break
            
            if low == 'help':
                show_help()
                continue
                
            if low.startswith('plot '):
                print(handle_plot(text))
                continue
                
            if '=' in text and not low.startswith(('limit', 'int', 'diff', 'plot')):
                print(handle_equation(text))
                continue
                
            if 'integral' in low or 'integrate' in low or '∫' in text:
                print(handle_integral(text))
                continue
                
            if low.startswith(('d/d', 'diff', 'derivative')):
                print(handle_derivative(text))
                continue
                
            if 'limit' in low:
                print(handle_limit(text))
                continue
                
            # Boshqa barcha holatlar
            print(handle_other(text))

        except KeyboardInterrupt:
            print("\nDastur to'xtatildi.")
            break
        except Exception as e:
            print(f"Dastur xatosi: {e}")

if __name__ == "__main__":
    main()
    