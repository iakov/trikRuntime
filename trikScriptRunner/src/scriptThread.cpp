/* Copyright 2014 CyberTech Labs Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License. */

#include "scriptThread.h"

#include <QtCore/QEventLoop>
#include <QtCore/QDateTime>
#include <QtQml/QJSEngine>
#include <QtQml/QJSValueIterator>
#include <QRandomGenerator>
#include <QJsonObject>

#include "threading.h"
#include <QsLog.h>

using namespace trikScriptRunner;

ScriptThread::ScriptThread(Threading &threading, const QString &id, QJSEngine *engine, const QString &script)
	: mId(id)
	, mEngine(engine)
	, mScript(script)
	, mThreading(threading)
{
}

ScriptThread::~ScriptThread()
{
}

void ScriptThread::run()
{
	QLOG_INFO() << "Started thread" << this;

	//QRandomGenerator::global()->seed(QDateTime::currentMSecsSinceEpoch());

	QJSValue result = mEngine->evaluate(mScript);

	auto resultQObject = result.toQObject();
	if (resultQObject != nullptr){
		if (QJSEngine::objectOwnership(resultQObject) == QJSEngine::JavaScriptOwnership){
			QJSEngine::setObjectOwnership(resultQObject, QJSEngine::CppOwnership);
		}
	}

	if (result.isError()) {
		const auto line = result.property("lineNumber").toInt();
		const auto &message = result.property("message").toString();
		const auto &backtrace = result.property("stack").toString();
		mError = tr("Line %1: %2").arg(QString::number(line), message);
		if (!backtrace.isEmpty()) {
			mError += "\n" + backtrace;
		}
		QLOG_ERROR() << "Uncaught exception with next backtrace" << backtrace;
	} else if (mThreading.inEventDrivenMode()) {
		QEventLoop loop;
		connect(this, &ScriptThread::stopRunning, &loop, &QEventLoop::quit, Qt::QueuedConnection);
		loop.exec();
	}

	mEngine.reset();
	QLOG_INFO() << "Ended evaluation, thread" << this;
}

void ScriptThread::abort()
{
	if (isEvaluating()) {
		mEngine->setInterrupted(true);
	}
	emit stopRunning();
}

QString ScriptThread::id() const
{
	return mId;
}

QString ScriptThread::error() const
{
	return mError;
}

bool ScriptThread::isEvaluating() const
{
	return mEngine && !(mEngine->isInterrupted());
}

// TODO: Fix design error. This slot is called on wrong thread (probably)
// mEngine must be accessed from the correct worker thread instead
void ScriptThread::onGetVariables(const QString &propertyName)
{
	if (mEngine != nullptr) {
		QJSValueIterator it(mEngine->globalObject().property(propertyName));
		QJsonObject json;
		while (it.hasNext()) {
			it.next();
			json[it.name()] = it.value().toString();
		}
		emit variablesReady(json);
	}
}
