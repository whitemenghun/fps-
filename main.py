#PFS 问题反馈系统
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g
from datetime import datetime

DATEBASE_URL = r".\db\feedback.db"


app = Flask(__name__)
app.debug=True

#将游标获取的Tuple根据数据库列名转化为dict
def make_dicts(cursor,row):
    return dict((cursor.description[i][0],value) for i, value in enumerate(row))

#获取(建立数据库连接)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATEBASE_URL)
        # db.row_factory = make_dicts
    return db


#执行SQL语句不返回数据结果
def execute_sql(sql, prms=()):
    c = get_db().cursor()
    c.execute(sql, prms)
    c.connection.commit()


#执行用于选择数据的SQL语句
# def query_sql(sql, prms=()):
#     c = get_db().cursor()
#     vlue = c.execute(sql, prms)
#     return (vlue.fetchone() if prms else vlue.fetchall()) if vlue else None

def query_sql(sql,prms=(), one=False):
    c = get_db().cursor()
    result = c.execute(sql,prms).fetchall()
    c.close()
    return (result[0] if result else None) if one else result




#关闭连接(在当前app上下文销毁时关闭连接)
@app.teardown_appcontext
def close_coonection(exeption):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pfs/')
def pfs():
    return render_template('base.html')

@app.route('/feedback/')
def feedback():
    sql = 'select ROWID, CategoryName from category'
    # coon = sqlite3.connect(DATEBASE_URL)
    # c = coon.cursor()
    # categories = c.execute(sql).fetchall()
    # c.close()
    # coon.close()
    categories = query_sql(sql)
    return render_template('post.html', categories=categories)


@app.route('/post_feedback/',methods=['POST'])
def post_feedback():
    # 如果当前请求的方法为post
    if request.method == 'POST':
        #获取表单值
        subject = request.form.get('subject')
        categoryid = request.form.get('category',1)
        username = request.form.get('username')
        email = request.form.get('email')
        body = request.form.get('body')
        releasetime = datetime.now()
        is_processed = 0

        # coon = sqlite3.connect(DATEBASE_URL)
        # c = coon.cursor()
        sql = "insert into feedback(Subject,CategoryID, UserName, Email, Body,IsProcessed, ReleaseTime)  values (?,?,?,?,?,?,?)"
        # c.execute(sql,())
        # coon.commit()
        # coon.close()
        execute_sql(sql,(subject, categoryid, username, email, body, is_processed, releasetime))
        return redirect('/')


@app.route('/admin/list/')
def feedback_list():
    # coon = sqlite3.connect(DATEBASE_URL)
    # c = coon.cursor()
    sql = "select f.ROWID,f.*,c.CategoryName from feedback f INNER JOIN category c ON c.ROWID=f.categoryID ORDER BY f.ROWID DESC "
    # feedbacks = c.execute(sql).fetchall()
    # coon.close()
    feedbacks = query_sql(sql)
    return render_template('feedback-list.html', items=feedbacks)

#删除功能
@app.route('/admin/feedback/del/<id>')
def delete_feedback(id=None):
    # coon = sqlite3.connect(DATEBASE_URL)
    # c = coon.cursor()
    sql = "delete from feedback WHERE ROWID = ?"
    # c.execute(sql,(id,))
    # coon.commit()
    # coon.close()
    execute_sql(sql,(id,))
    return redirect(url_for('feedback_list'))

#编辑页面
@app.route('/admin/edit/<id>')
def edit_feedback(id = None):
    # coon = sqlite3.connect(DATEBASE_URL)
    # c = coon.cursor()


    sql = 'select ROWID, CategoryName from category'
    # categories = c.execute(sql).fetchall()
    categories = query_sql(sql)

    #获取当前id的信息,并绑定至Form表单,以备修改
    sql = 'select ROWID,* from feedback WHERE rowid = ?'
    # current_feedback = c.execute(sql,(id,)).fetchone()
    current_feedback = query_sql(sql,(id,))

    # c.close()
    # coon.close()
    return render_template('edit.html', categories=categories, item=current_feedback)

#编辑功能
@app.route('/admin/save_edit',methods=['POST'])
def save_feedback():
    if request.method == 'POST':
        # 获取表单值
        is_processed = 1 if request.form.get('isprocessed',0) == 'on' else 0
        reply = request.form.get('replay')
        rowid = request.form.get('rowid',None)

        sql = 'update feedback set Reply = ?,IsProcessed = ? WHERE rowid = ?'
        # coon = sqlite3.connect(DATEBASE_URL)
        # c = coon.cursor()
        # c.execute(sql,(reply, is_processed, rowid))
        # coon.commit()
        # coon.close()
        execute_sql(sql,(reply, is_processed, rowid))

        return redirect(url_for('feedback_list'))








if __name__ == '__main__':
    app.run()