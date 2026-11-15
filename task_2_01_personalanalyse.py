print(df['employees'].columns)

# 1. Mitarbeitende mit bonus > base_salary ermitteln.
emp = df['employees'][['employee_id', 'first_name', 'title','last_name', 'region', 'manager_id']]
emp_salaries = df['employee_salaries'][['employee_id', 'base_salary','bonus',]]

data = pd.merge(emp, emp_salaries, on='employee_id')

anomaly = data[data['bonus'] > data['base_salary']]

print("Auffällige Bonuszahlungen: \n", anomaly)

# 2. Grundgehalt und Bonus mit einer Referenzlinie y = x darstellen.

plt.figure(figsize=(10,5))
plt.scatter(data['base_salary'], data['bonus'], alpha=0.6, color ='green')
plt.plot(data['base_salary'].min(), data['base_salary'].max(),
                data['base_salary'].min(), data['base_salary'].max(), color ='red', linestyle='--', label = 'y = x')
plt.xlabel("Grundgehalt")
plt.ylabel('Bonus')
plt.title("Grundgehalt und Bonus")
plt.show()

# 3. Durchschnittliche Boni nach Region und Position berechnen.

avg_bonus_region = data.groupby('region')['bonus'].mean().round(2)
avg_bonus_title = data.groupby('title')['bonus'].mean().round(2)

print("Durchschnittlicher Bonus nach Region: \n", avg_bonus_region)
print("Durchschnittlicher Bonus nach Position: \n", avg_bonus_title)

# 4. Gehaltsunterschiede innerhalb derselben Position als Prüfhinweis vergleichen.

salary_var = data.groupby('title')['base_salary'].agg([ 'min','max','mean', 'std']).round(2)
salary_var['range'] = (salary_var['mean'] - salary_var['min']).round(2)

print("Gehaltsunterschiede nach Position: \n",salary_var.sort_values(by='range', ascending=False))
