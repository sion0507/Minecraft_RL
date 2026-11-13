# 실행 기록

## 2026-11-12 — #51 PR #53 병합·이슈 종료·로컬 main 동기화 완료

사용자의명시적현재결과게시/종료요청을완료했다. 구현/결과커밋 `61dd164d27e959e56772167f85a389f89c36c7c8`를featurebranch에commit/push하고 PR **#53 MERGED**(https://github.com/sion0507/Minecraft_RL/pull/53 ,17:34:54 KST),merge `a656c200d633c1db7d4ed56a54df6f6df759549e`를확인했다. `Closes #51`에따라 **#51 CLOSED/completed**(https://github.com/sion0507/Minecraft_RL/issues/51 ,17:34:56 KST). 종료댓글 https://github.com/sion0507/Minecraft_RL/issues/51#issuecomment-6818897546 에판정/진단/한계/검증을기록했다. 로컬main도origin/main의병합결과로fast-forward했고최종상태문서commit/push를이어수행한다. 초기ff명령은샌드박스의.git/ORIG_HEAD쓰기차단으로실패했으나승인된동일명령으로정상완료,원격상태나자료를되돌리지않았다.

**게시 검증:** pytest316개/234.93초·strictmypy54파일·git diff --check통과,독립코드/결과review Critical/Important0. 검사커밋61dd164와merge커밋a656c20의전체tree hash는모두 `7e138177aaa8befc3bff9e409b01ce950675e5c1`로동일하다. 원격PR은mergeable/CLEAN이었고statusCheckRollup/commitstatus는빈목록으로원격CI설정없음. 최종상태문서변경만추가하므로개발검사/게임을반복하지않았다.

**종료한 범위:** 파일럿전용구현·원래gate중단·사용자예외4096/32update·고정96확률+0.037764/“판정 보류”·보조4/10→5/10·고정7B24응답·critic오프라인36checkpoint/24run/768rollout검산과두실패/복구/비용을전부기록했다. canonical결과는 `docs/results/issue-51.md`,seed/rollout별수치는 `docs/results/issue-51-critic-summary.json`이다. 초기gate=false·불완전표본·원시자료·공개초기head복원과실험한계를보존했고본학습/critic변형적용/새월드검증을완료로표시하지않았다.

**PDF·원자료:** 사용자요청으로#51의기존report/code-guide PDF두개삭제·새PDF생성0,다른이슈37PDF및ignored artifacts/runs/checkpoints/worlds는보존했다. 원시trace/특징/가중치/로그를Git에넣지않았다. 이번마무리에서새게임·GPU/모델·유료API진단·본학습을추가하지않았다. 사용자승인작업완료이며추가연구실행/설정채택은별도결정이다.

## 2026-11-12 — #51 게시·병합·종료 승인, 최종 개발 검사와 기록 정리 완료

사용자가 #51의현재구현·실제파일럿·7B확인·후속critic오프라인평가까지기록해commit/push/PR/merge/이슈종료를명시승인했다. 이전게시금지는이범위에서대체된다. 현재는게시준비완료이며원격PR/merge/이슈상태는다음완료절에서확인한다. 본학습·critic변형채택·새게임/모델/유료API진단은추가하지않았다.

**개발검사(새 실행):** `UV_CACHE_DIR=.cache/uv .tools/uv run --locked --no-sync pytest` 전체316개/234.93초통과,동일uv의strict `mypy .`54파일통과. tiny/mock/fixture 개발검사이며새Minecraft게임이나공개모델학습효과검증이아니다. `artifacts/issue-51/publication-{pytest,mypy}.txt`에보존했다. 독립read-only검토는공개CLI→파일럿→episode/학습/보상/신호/복원및회귀검사를연결해확인했고Critical/Important0,수치문서도원본summary/aggregates와대조했다. 단계별누적시간3024.90초에정보감사777.29초를다시더하지않음을확인했다.

**기록:** `docs/results/issue-51.md`에전체결과/실패/복구/한계를, `docs/results/issue-51-critic-summary.json`에모든등록step·3seed·32rollout별critic수치/원자료hash를기록했다. README/CONTEXT/DECISIONS/#16/#17/#18/#20인계를최신화했다. 실제판정은여전히“판정 보류”이며보조4/10→5/10·원래gate=false·초기복원true·critic추가계산효과와미검증범위를구분했다. 원시trace/특징/가중치/실행로그는Git제외로보존한다.

**PDF(사용자 지시):** reports/issue-051-T14B-report.pdf와code-guide.pdf두개삭제확인,새PDF생성0·다른이슈PDF37개보존. 삭제전hash/크기는 `artifacts/issue-51/publication-pdf-deletion.json`에만기록했다. 아래PDF존재/생성문구는당시이력이다.

## 2026-11-12 — #51 critic 오프라인 복구 완료·등록36checkpoint/24온라인실행 검산 완료

**실제 실행:** `artifacts/issue-51/critic-offline-20261112-141206/recovery-20261112-164118/`, 2026-11-12T16:46:16.626665+09:00→2026-11-12T16:47:48.683774+09:00, background exit0·전체92.06초. 앞선실패의138shard/4096특징을전부재사용하고마지막선택되지않은bootstrap상태1개(후보1개)만새로인코딩했다(모델로드포함10.72초). 수집결정은4096개/완료MC4045개로유지했고경계상태를수집/학습정답에추가하지않았다. 원본실패보고·비용은보존했다.

**수정·검증:** artifacts진단의다음상태연결에외부bootstrap특징인덱스를지원하고,fit입력행렬에그1개특징만별도로붙였다. src는변경하지않았다. 경계회귀검사2개RED→GREEN·기존MC/GAE자가검사통과. 원본summary와32rollout의당시완료/누적MC표본수가모두일치한다. 저장예측으로768개rollout EV/합산EV,24run/36checkpoint/3seed/두분할/모든등록step,592대8404gradient수,동일seed·입력네방식의초기256예측동일,미래MC정답제외·paired차이/등록기준을별도CPU검산했다. protocol원문은바이트동일하고결과를보고설정/checkpoint를고르지않았다.

**기준 재현:** 주검증n1007 저장critic EV0.184019,보조n1037 0.161146,결정1024이후n3055 합산0.213676. 선형기준은주분할목표만0.200509/+시간·보유량0.354391/+거리0.492807,보조는0.342244/0.500093/0.595704다. 주분할학습3038/검증1007은103번째episode가양쪽에걸리고,보조학습3008/검증1037은episode중복0이다.

**고정 MC 적합(실제GPU,3seed 평균±SD):** head seed11051/22051/33051,LR1e-4·batch32·BF16 autocast/FP32파라미터·TF32off,기존구조256/GELU/1. 스칼라는진행도·visible원천거리/32·남은틱/1800이다.

| 분할 | step | 현재 입력 EV | +스칼라 EV |
|---|---:|---:|---:|
| 주 시간순 | 128 | 0.331 ± 0.015 | 0.355 ± 0.023 |
| 주 시간순 | 512 | 0.411 ± 0.011 | 0.446 ± 0.003 |
| 주 시간순 | 2000 | 0.447 ± 0.009 | 0.486 ± 0.006 |
| 보조 episode | 128 | 0.378 ± 0.016 | 0.391 ± 0.011 |
| 보조 episode | 512 | 0.442 ± 0.007 | 0.493 ± 0.009 |
| 보조 episode | 2000 | 0.491 ± 0.006 | 0.565 ± 0.009 |

**온라인 순차 재현(결정1024이후합산 예측EV,3seed 평균±SD):** 첫128결정MC32epoch워밍업공통,이후미래return없이학습하고각rollout학습전예측을채점했다. actor는학습하지않고기록된행동흐름을고정했다.

| 온라인 방식 | 현재 입력 EV | +스칼라 EV | optimizer step |
|---|---:|---:|---:|
| 최신GAE4epoch | 0.206 ± 0.074 | 0.209 ± 0.028 | 592 |
| 최신MC4epoch | 0.173 ± 0.052 | 0.229 ± 0.031 | 592 |
| 누적MC동일step | 0.241 ± 0.064 | 0.235 ± 0.005 | 592 |
| 누적MC4epoch | 0.329 ± 0.066 | 0.387 ± 0.033 | 8404 |

**통제 비교:** 뚜렷함은평균차이≥0.05·세paired seed모두양수로실행전에등록했다.

| 입력 | 비교 | EV 평균 차이 | seed 최소–최대 | 뚜렷함 |
|---|---|---:|---:|---|
| 현재 | ①목표값 | -0.032 | -0.144~+0.119 | 미통과 |
| 현재 | ②재사용 | +0.068 | -0.041~+0.156 | 미통과 |
| 현재 | ③계산량 | +0.088 | +0.009~+0.157 | 통과 |
| 스칼라 | ①목표값 | +0.020 | -0.035~+0.095 | 미통과 |
| 스칼라 | ②재사용 | +0.006 | -0.043~+0.032 | 미통과 |
| 스칼라 | ③계산량 | +0.152 | +0.112~+0.177 | 통과 |

**해석·미검증:** 현재입력MC적합0.447>저장예측0.184로현재구조/입력에도추가예측력이있고학습방식·자료·계산량을검토할근거가있다. 스칼라추가주분할2000step+0.038은기준미달,보조+0.075는통과해양쪽512/2000모두요구한견고한개선기준은불통과다. ①목표값·②동일gradient재사용은두입력모두일관된개선을확인하지못했고,③누적MC의592→8404step(약14.2배)추가계산은둘다통과했다. MC목표/재사용만으로좋아진다는가설은이번결과로확정하지않는다. ①에는MC미완성꼬리표본차이,②③에는셔플epoch/복원추출방식차이도있다. seed SD는환경표본의신뢰구간이아니며,고정월드·기록정책자료의값예측진단이어서새월드일반화·실제actorPPO효율/성공률개선은미검증이다. EV상한을주장하거나설정을채택하지않았다.

**자원·보존:** 이번GPU계산/감사90.67초·supervisor전체92.06초,선행추론538.38+실패7316.47+복구합계7946.91초(2시간12분26.91초;준비/CPU검산/기록시간별도). RAMpeak5750.6MiB,PyTorch GPU allocated/reserved peak2543.4/2598.0MiB. src·원본trace·summary·파일럿head hash모두불변. 새게임/bridge/API/7B/본학습0,commit/push/merge/이슈종료/PDF갱신없음. GPU작업종료확인. 본학습초기화에진단head/경험을사용하지않는다.

**산출물:** 같은폴더의`report.md`,`results.json`,`aggregates.json`,`online-rollouts.csv`,`online-rollouts-mean.csv`,`results-verification.json`,`final-audit.json`,`encoding-audit.json`,`cache-read-audit.json`,회귀/CPU검사로그와실행로그. 기존Claude기록및앞선실패절은아래에그대로보존했다.

## 2026-11-12 — #51 critic 오프라인 진단 실패·전체 특징 보존·비교 학습 미실행

**실패(실제):** `artifacts/issue-51/critic-offline-20261112-141206/`, background 14:25:38→16:27:35 KST, exit1, elapsed 7316.47초. GPU 특징 추출138episode/4096결정 및138개 원자shard 저장은 완료했지만, 이어진 next-state 연결 assertion에서 멈춰 static checkpoint0/예정36·온라인run0/예정24이다. 결과/집계/최종완료audit는 생성되지 않았다. 새로 만든 `report.md`는 성공 보고가 아닌 실패 보고다.

**확인된 원인:** 진단 스크립트가 모든 valid+bootstrap 전이의 next state를 다음 선택 행에서 찾을 수 있다고 가정했다. 유일한 누락은 마지막 결정번호4095(episode138, pilot:logs)다. 다음상태 obs_id `8c76569a-8525-4264-ac54-d68eb256b0e5:1228`, 남은572틱·후보1개는 원본transition.next_state에 실제 존재하지만,4096결정 상한 뒤라 선택행/추출특징에는 없다. 마지막 bootstrap 상태 특징의 별도 보관을 빠뜨린 진단 코드 결함이며 게임 오류·GPU OOM·원자료 손상이 아니다. 해당 assertion을 삭제하거나 next value를0으로 임의 대체하지 않았다.

**CPU 감사만 추가 실행:** 저장shard138개/4096행의 특징·mask·context·pooling 크기와 유한값·순서를 검사했다. 저장된 critic 예측 재현 최대절대오차는4096개 모두0. 유효완료MC4045개. trace138개·원본summary·파일럿head·src Python의SHA256은 착수 때와 모두일치한다. 마지막next_state의원문과key일치도확인했다. `failure-audit.json`, `cached-rows-audit.json`, `logged-baseline-rollouts.csv`에 근거를 보존했다. 새로운 GPU추론·critic학습·선형재적합·실험재시도는하지않았다.

**기존 저장예측 기준 재현:** 주 시간순검증 n1007 EV0.184019(기존0.184), episode단위보조검증 n1037 EV0.161146, 결정1024이후합산 n3055 EV0.213676(기존0.214). 이 값은 저장예측을다시채점한것이며 새critic의성능이아니다. 과거선형기준0.201/0.354/0.493은참고값으로만유지,이번에는재적합하지않았다.

**미실행:** 양쪽분할·입력2종·seed11051/22051/33051의 static128/512/2000 checkpoint 전부, 온라인 최신GAE4epoch/최신MC4epoch/누적MC동일gradient수/누적MC4epoch 전부 미실행. 따라서①목표값·②재사용·③계산량의차이와seed범위,등록상뚜렷함은전부미측정이다. MC완료꼬리/미래정답유출방지의온라인실행검증도남아있다. 설정채택·EV상한·새월드일반화·실제PPO개선은판단하지않는다.

**비용·운영:** background7316.47초+앞선의도적중단추론538.38초=7854.85초(2시간10분54.85초). 초기장치표기기동실패약2.59초·준비/기록시간은별도다. 최대관측RAM5571.4MiB(약5.44GiB),GPUpeak최종계측미실행. 완료알림queue는returncode0으로1회전송됐다. 게임·bridge·모델API·7B·본학습0,src수정/commit/push/merge/이슈종료/PDF갱신없음. 사용자지시대로자동재시도하지않았다. 향후복구는저장된4096특징을재사용하고마지막경계상태를별도로처리해검사한뒤미실행비교를시작하는별도작업이며,아직수정·실행하지않았다.

## 2026-11-12 — #51 후속 critic 오프라인 진단 백그라운드 실행 중(온라인 통제 변형 2개 추가 승인)

**실제 착수·미완료:** `artifacts/issue-51/critic-offline-20261112-141206/`, 시작 2026-11-12T14:25:38.644536+09:00, supervisor PID 89308/자식 89309. 저장된138 trace·4,096결정의 공개NanoJev frozen특징을GPU에서 순차 재인코딩한다. 관측 전체를 누적하지 않고 후보특징·mask·context·스칼라만 남기며 새 실행은 에피소드별 원자checkpoint를 저장한다. 현재 새critic 비교 결과는 아직 미실행·미확정이다.

**사전 등록:** `protocol.json`(원본 `protocol-v1.json` 보존). 주 결정번호<3072/≥3072, 보조episode seed51051의35개검증, head seed11051/22051/33051, static step128/512/2000. 뚜렷함은 평균EV차이≥0.05·세paired seed모두양수, 입력추가견고함은 양쪽분할의512/2000모두통과일때다. 검증값으로 설정/checkpoint를 고르지 않는다. 기존Claude 점검절은 아래원문그대로보존한다.

**온라인 네 변형(입력2종 각각):** 최신GAE4epoch / 최신완료MC4epoch(사용자추가) / 누적완료MC+최신GAE와동일gradient step(사용자추가) / 누적완료MC4epoch. 첫128결정MC32epoch워밍업은공통고정. ①최신MC−최신GAE, ②누적MC동일step−최신MC, ③누적MC4epoch−누적MC동일step의평균·seed최소/최대·개별값을보고한다. MC미완성꼬리제외때문에①에는사용표본차이도섞인다. 기록된행동흐름을고정하며actor를학습하지않는다.

**검사·비용·한계:** MC terminal/취소/무효 및공개decisions·GAE와의작은수치자가검사통과. 선행추론8episode/249결정까지저장critic값재현오차0·첫episodeMC일치,RAMpeak5.57GB. 백그라운드전환을위해선행추론538.38초를의도적으로중단했고비용/로그를`foreground-attempt.json`에보존했다. 선행extractor에episode checkpoint가없어특징을다시계산한다. 최초자가검사필드누락·GPU장치문자열기동실패로그도보존,실험설정변경은아님. 현재속도상전체특징추출약1.5–2시간예상(미실측추정);추가head통제는그뒤실행한다. 최종보고는baseline0.184/후반pooled0.214재현,선형기준,분할/step/seed별EV,네온라인변형및①②③,전체시간/원자료불변감사를포함한다. 같은시작return sd로EV상한을확정하지않는다.

**운영:** supervisor가자식종료를기다려정상/실패완료이벤트를현재대화에1회전송한다. 자동실험재시도없음. 소스변경·새게임·bridge·API·7B·본학습·채택·commit/push/merge/이슈종료·PDF갱신없음. 결과후새절로기록하고사용자에게수치/한계를보고한다.

## 2026-11-12 — #51 사용자 예외 학습 4,096결정 완료·사전 등록 판정 "판정 보류"

**실행(실제):** `artifacts/issue-51/exception-20261112-024101/`, 02:41:01→11:14경 KST, supervisor `completed`/returncode 0, 경과 30,794.9초(8시간 33분), native crash 0, 실행 중 고정 소스·snapshot·시계 인증 불변(`sources_unchanged=true`), 원본 참조 자료 불변(`reference_unchanged=true`). API·7B 계획 호출·본 학습 결정 0. 원래 gate=false와 `mine_oak_log` 초기 신호 판정 불가는 그대로이며 이 학습은 사용자 예외 실행이다.

**학습:** 4,096결정/32 update/미반영0, 학습 에피소드 138(유효 138, 성공 54), 에피소드 합 27,568초. 워밍업은 첫 rollout 사후 EV 0.605로 종료(`ev_threshold`, critic-only 128결정). actor 전이 2,871, 유효 4,073, 제외 23. 백본 불변, Choice·critic 변경. 학습 중 critic EV는 update별 −0.20–0.77로 크게 흔들렸다(마지막 4개 0.718/0.240/0.289/0.326).

**주 판정(고정 96상태, 사전 등록):** 좋은 후보 확률 0.41299→0.45076, **+0.0378 → "판정 보류"**(+0.03 이상 +0.10 미만). 2,048결정(update 16) 보조값 0.43683(+0.0238). 정규화 엔트로피 0.9905→0.9544. 종류별(초기→4,096, 균등 몫): move_oak_log 15상태 0.220→0.276(0.219), mine_oak_log 7상태 0.641→0.716(0.571), move_stone 44상태 0.501→0.523(0.505), mine_cobblestone 30상태 0.327→0.370(0.298). 저장된 initial/update-16/update-32 head를 GPU에서 다시 읽어 고정 96상태로 재계산해 같은 값을 얻었다. 확률은 update 20–26에 0.42 근처에 머물다 update 27–32에 0.428→0.451로 올랐으므로 마지막 값이 학습 길이에 민감할 수 있다(해석, 미검증).

**보조 평가(성공률은 판정에 쓰지 않음):** 후10 성공 5/10(15002·15003·15005·15007·15009), 초기10(원본 재사용) 4/10. 10슬롯 모두 1회 시도·서버 오류 0·재시도 0. 15005는 1,800틱 마지막 결정에서 조약돌3을 채워 성공. 같은 시드 첫 분기: 정책 8, 드롭 시점 2, 지도 차이 0. 정책 분기 지점의 같은 상태 후보 확률 최대 변화는 0.011–0.147이며 sampling 시드가 같아도 작은 확률 변화로 뽑힌 후보가 바뀐 것이다. 4/10 대 5/10은 차이를 주장할 수 없다.

**보조 진단:** 학습 trace 신호 확인은 네 종류 모두 좋은 선택 평균이 높았다(mine_oak_log good147/bad61, 0.670 대 0.624). 첫 결정 분포는 move 0–7에 15–22로 고르며 #49의 move:5 쏠림(23/73)은 재현되지 않았다(move:5 22/138). 별도 critic 적합(학습 3,868/검증 96, 위치·인벤토리 분리) 검증 EV 128 step 0.163, 2,000 step 0.297로, 고정 상태에서도 critic 구조의 적합이 약하다.

**원시 감사:** 학습 trace 138개에서 선택·step·reward 각 4,096, 완료 요약 138, 무효/일시정지 미인증 step 0, 모든 reset 빈 인벤토리·0/1800틱. 후10 trace의 직접 획득·틱·완료 사유가 요약과 일치. update-32 head hash = 최종 hash, 백본 = 공개 백본, 고정 상태 파일 = 원본과 바이트 동일, 종료 시 초기 head 복원 true(공개 가중치를 seed 11015로 읽으면 초기 hash와 일치. critic head는 seed로 새로 초기화되는 부분). `rpc-errors-new.log`에 06:15 KST 서버 기동 시간 초과 1건과 bridge 내부 기동 재시도 1건이 있었고 해당 에피소드 시작 전이라 결과에 영향 없음. 메모리는 학습 프로세스 최대 관측 10.5GB, swap 0.

**추가 오프라인 분석(2026-11-12, 게임 0, GPU 재계산·trace 재읽기):** 고정 96상태별 변화는 69/96 상승, 평균 +0.0378·중앙값 +0.0417·표준편차 0.071, 상태 bootstrap 95% 구간 +0.024–+0.052, 원본 에피소드 10개 단위 bootstrap +0.027–+0.048(+0.10 이상 확률 0, +0.03 미만 확률 0.07). 종류별 상승 수: mine_cobblestone 29/30, mine_oak_log 7/7, move_oak_log 11/15, move_stone 22/44. 초기→최종 분포 거리(TV) 평균 0.099, 최대 후보 확률 평균 0.165→0.218. 이동 후보 자리별 평균 확률은 move:3 0.137→0.162, move:5 0.136→0.166, move:0 0.121→0.136으로 오르고 move:1/2/6은 0.02–0.03 내렸다(설명보다 방향 자리에 실린 변화가 섞여 있음, 고정 월드 적응 가능성). 학습 4,096결정의 on-policy 좋은 후보 초과 확률(균등 몫 대비)은 512결정 구간별 +0.018/+0.013/+0.027/+0.029/+0.043/+0.025/+0.038/+0.075, 네 종류 모두 첫 1,024결정보다 마지막 1,024결정이 +0.03–+0.05 높다. 학습 에피소드 성공은 구간별 8/4/10/7/6/3/8/8(각 17–18개)로 추세가 없다. 해석: 등록 방향의 움직임은 잡음이 아니지만 크기가 작고 행동 성과로는 나타나지 않았다. 등록 판정 "판정 보류"는 바꾸지 않는다.

**critic 오프라인 점검(2026-11-12, trace만 읽음, 게임·GPU 0):** 요약의 update별 critic EV는 그 rollout을 학습한 직후 같은 자료로 잰 값이다. trace의 선택 시점 예측값(그 rollout 학습 전)으로 다시 잰 예측 EV는 update 1에서 0.16(보고값 0.605), update 9–32 rollout별 평균 0.32(보고값 평균 0.395), 1,024–4,095결정 전체를 합쳐 재면 0.214다. 워밍업은 같은 자료 EV로 기준을 넘어 128결정에 끝났다. return 구성: pilot:logs n=1,320 평균 0.712·sd 0.331, pilot:pick n=875 평균 0.998·sd 0.001, pilot:stone n=1,850 평균 0.505·sd 0.336, 전체 sd 0.351, 거리 potential 항 sd 0.127. 항상 같은 에피소드 시작 상태에서의 return도 sd 0.255(0.09–1.04, n=137)로 흩어진다. 앞 3,072결정으로 맞추고 뒤 1,007결정으로 잰 선형 최소제곱 EV: 하위 목표만 0.201, +남은 시간·보유 개수 0.354, +거리 potential 0.493, 같은 구간 실제 critic 0.184. rollout당 에피소드는 약 4.3개다. 해석: critic은 하위 목표 구분 수준에 머물렀고, 관측에서 얻을 수 있는 단순 수치만으로도 더 잘 맞출 여지가 있으나 같은 상태의 결과 분산 때문에 상한은 낮다. critic 변경은 구현·실행하지 않았다.

**PDF:** reports/issue-051-T14B-report.pdf(2쪽)·code-guide.pdf(2쪽)를 최신 실제 결과로 교체했다. 한글 추출·WenQuanYi 글꼴 포함·4쪽 전체 렌더 가독성 확인, reports Git 추적 0. 생성기는 세션 scratchpad에만 있다.

**미실행·남은 일:** 판정 후 결정(PLAN §6.4 다른 행동 모델·A/B 축소·보상 조정·추가 파일럿)은 사용자 결정. 파일럿 head·경험은 본 학습 초기화·30,000결정에 쓰지 않는다. commit/push/merge/이슈 종료 없음.

## 2026-11-12 — #51 사용자 예외 학습 4,096결정 재실행 시작(메모리 수정 후)

사용자가 "시작해"로 공개 초기값에서의 새 4,096결정 재실행을 명시 승인했다. 착수 전 확인: 실행 중 프로세스 없음, RAM 여유 26GB, GPU 476MiB 사용. 다른 세션이 20:11에 수정한 `signal_pilot.py`(이력 지도 제거·참조 head 거절 전 복원 순서)는 `user-exception-source-manifest.json`의 31파일과 모두 일치했다. 그 세션의 전체 pytest(20:07)가 마지막 수정보다 앞서므로 현재 소스로 `tests/test_signal_pilot.py` **19개 통과/80.13초**, strict **mypy 54파일** 통과를 다시 확인했다(`artifacts/issue-51/relaunch-{targeted,mypy}.txt`).

**02:41:01 KST** `artifacts/issue-51/exception-20261112-024101/`에서 detached supervisor **PID 4854**(자식 4856)로 시작했다. 원본 초기10·정보감사·고정96은 재사용하고 재실행하지 않는다. 02:46 확인에서 참조 검증 통과, `fixed-00.json` 기록, `signal-train-1` 진행, 학습 프로세스 RSS 5.15GB였다. 1차 중단 실행(`exception-20261111-184420`)은 폐기 경험으로 보존한다. 메모리 확인: 03:12(약260결정) RSS 8.09→8.03GB(45초), 03:26 update3 직후(약384결정) RSS 8.97GB·swap0·시스템 여유17.7GB. 1차는 같은 결정 수에서 13–16GB 이상으로 선형 증가했으므로 누적 증가는 해소된 것으로 보이며, 남은 변동은 rollout 128건 범위다(최대치는 종료 후 확정). 예상 종료는 약 10:30 KST(추정). commit/push/merge/이슈 종료 없음.

## 2026-11-11 — 외부 세션 예외 학습 중단 확인·재실행 승인 대기

사용량제한후복귀해공유폴더를대조하던중다른Claude세션의실제예외학습을확인했다. `exception-20261111-184420`은18:44:20시작→4292.948초(71분32.948초)뒤exit130/KeyboardInterrupt로종료했다. 원시20attempt에서reset20·선택581·step/reward/transition580·완료summary19·PPO4를확인했다. 마지막20번째attempt는선택1/반환step0으로불완전하다. 580전이중512는4rollout update에사용,68은미반영이다. 수집actor331중update에실제사용된actor281(100+89+92),첫128은critic-only. 학습에피소드완료19중8성공이다. 첫update MC EV0.644로워밍업종료,512결정고정확률0.412489(초기0.412993)이나4096/2048미실행으로최종판정미판정이다. 후10은모두미실행이며on-disk요약은중단전snapshot이라최종초기head복원은미확인이다. 실제OOM kill의근거는없으며직접종료근거는KeyboardInterrupt다. 원본로그/중간head/비용은그대로보존한다(원시감사 artifacts/issue-51/exception-interrupted-audit.json).

다른세션의메모리보완(누적history의관측지도/next_state제거,MC식별자·features/context·위치/인벤토리보존)을보존·검토했다. 공개PPO는원래rollout을사용하며누적critic진단만축약본을쓴다. 독립검토중요미해결0,전체pytest316/217.19초·mypy54·diff통과. 참조head거절전복원파일저장순서결함도RED재현후수정했고잘못된참조/사유누락/다른신호실패거절과전체hash복원검사를통과했다. 현재확정초기고정96과rollout약128지도는유지하므로실제RAM최대치는미측정이다.

초기10/정보감사/원래gate=false·mine_oak_log good7/bad0/초기고정96는불변이다. 자료재사용안전검사는성공했으나**중복학습은시작하지않았다**. 정확한중간재개용optimizer/RNG가없으므로등록4096완료에는공개초기에서새학습이필요하다. 자동재시도없음원칙과기존실패/비용보존을명시해사용자에게새4096재실행승인을질문했고대기한다. PDF는사용자지시대로보류,commit/push/merge/이슈종료없음.

## 2026-11-11 — #51 사용자 예외 학습 1차 중단(메모리 결함)·수정, 재실행은 사용자 결정 대기

**실제 실패:** `exception-20261111-184420` 실행은 **19:55 KST에 580결정/4,096(학습 에피소드 19개 완료, 20번째 진행 중, update 4/32)에서 중단**했다. 판정·2,048 보조값·후10·보조 critic 적합·분기 분석은 모두 **미실행**, 최종 판정은 **미판정**이다. 서버 오류·native crash·API 호출 0, 경과 4,292.9초(학습 에피소드 합 3,955초).

**원인(구현 결함):** `SignalLearner.history`가 MC 정답·critic 진단용으로 모든 결정의 `State`를 보관했는데, 반경32 관측 하나가 메모리에서 약 30MB(지도 24,685칸, JSON 3.0MB)다. 학습 프로세스가 RSS 24.0GB+swap 1.4GB까지 분당 약 450MB씩 늘었고 시스템 여유 2.3GB·swap 3.9GB만 남아, Claude Code가 종료 대기 셸을 메모리 압박으로 회수했다. 4,096결정에는 약 195GB가 필요해 완료할 수 없었으므로 이 세션이 학습 프로세스에 SIGINT를 보내 종료했다(returncode 130). bridge/서버 잔류 프로세스 없음, 고정 소스·snapshot·시계 인증 불변(`sources_unchanged=true`). mock 관측은 작아서 개발 검사와 이 세션의 사전 검토·GPU 점검이 이 결함을 잡지 못했다.

**남긴 부분 자료(폐기 경험, 판정 근거 아님):** 학습 trace 20개(마지막은 미완), `update-01~04` head, `fixed-00~04.json`, 에피소드 19까지의 `summary.json`. 워밍업은 첫 rollout에서 사후 EV 0.644로 종료(`ev_threshold`), 이후 update 2–4의 critic EV 0.320/0.326/0.219, actor 전이 331. 고정 96상태의 좋은 후보 확률은 0.4130→0.4130→0.4113→0.4119→0.4125(update 0–4)로 사실상 변화 없음. 학습 에피소드 성공 8/19. 580결정은 판정 시점(4,096)의 14%이며 등록 판정에 쓰지 않는다.

**수정:** 이력에는 지도를 비운 관측 사본과 `next_state=None`만 남긴다(`signal_pilot.py` `SignalLearner.update`). MC 정답·critic 입력(특징/마스크/context)·위치·인벤토리 키는 그대로다. 보상·후보·PPO·gate·평가·설정은 바꾸지 않았다. RED→GREEN `test_signal_history_drops_observed_maps_but_keeps_mc_and_critic_inputs`, 전체 **pytest 316개/212.22초**, **mypy 54파일** 통과(`artifacts/issue-51/memory-{red,green}.txt`, `memory-fix-{pytest,mypy}.txt`). 실제 GPU 점검(게임 0): 실제 크기 상태로 이력 816건을 쌓는 동안 RSS 5.639→5.645GB(+약 6MB). 예상 상시 사용량은 모델+고정96상태(약 2.9GB)+rollout 128건(약 3.8GB)이다(추정, 실제 4,096결정 미검증).

**미실행·대기:** 같은 등록 설정으로 처음부터 다시 실행할지는 추가 실제 실행이므로 사용자 결정을 기다린다. 자동 재시도하지 않았다. PDF는 실제 결과 최신본이 아니다. commit/push/merge/이슈 종료 없음.

## 2026-11-11 — #51 사용자 예외 학습 4,096결정 백그라운드 시작

Codex 세션이 사용량 한도로 멈춘 뒤 Claude Code 세션이 이어받았다. 이어하기 구현(`--initial-evaluation-reference`+`--signal-exception-reason`, 출력 `signal-user-exception/`)은 Codex가 작성했고 이 세션은 코드를 바꾸지 않았다.

**개발 검사(mock):** 전체 pytest **315개 통과/210.24초**, strict mypy **54파일 통과** (`artifacts/issue-51/exception-{pytest,mypy}.txt`).

**검토:** 별도 하위 에이전트는 쓰지 않았다. 작성자(Codex)와 다른 이 세션이 이어하기 경로·MC 워밍업·보조 critic·참조 검증을 읽기 전용으로 검토했고 실행을 막을 결함은 찾지 못했다. 남은 위험: 학습 중 서버 오류는 등록 설계대로 재시도 없이 학습을 중단하고 후10을 미실행으로 남긴다. 중간 이어하기는 없다.

**실제 GPU 사전 점검(게임·API 0):** 공개 NanoJev로 원본 참조 검증 통과(고정 이후 변경 소스는 cli.py·signal_pilot.py뿐), 고정 96상태 재인코딩이 원본 지표를 1e-6 안에서 재현(좋은 후보 확률 0.4130, 균등 몫 0.4006, 엔트로피 0.9905), 합성 전이 48개로 CUDA 워밍업 critic 적합·보조 critic 2,000 step 경로가 오류 없이 끝나고 초기 head hash가 복원됨을 확인했다. 합성 전이의 수치는 학습 근거가 아니다.

**실제 실행:** **18:44:20 KST** `artifacts/issue-51/exception-20261111-184420/`에서 detached supervisor **PID 551667**(자식 551669)로 시작. 원본 초기10·정보감사·고정96은 재실행하지 않고 재사용한다. 18:49 기동 확인 1회에서 참조 검증 통과·`fixed-00.json` 기록·`signal-train-1` 진행을 확인했다. 예상 소요는 학습 약 7.4시간+후10 약 0.5시간(추정). 원래 gate=false와 `mine_oak_log` 초기 신호 판정 불가는 그대로다. 결과·판정·PDF 갱신은 종료 후 기록한다. commit/push/merge/이슈 종료 없음.

## 2026-11-11 — #51 원래 D 감사 결과·사용자 예외 학습 승인

원래D real-20261111-171623는정보감사exit0(35fixture/23범위),초기10실행4성공/6시간상한실패·291결정·15826틱·후10미실행. 원목/나무곡괭이완료각9/10. gate=false는mine_oak_log good7/bad0표본부족이며나머지3종류평균차양수. 학습/PPO/워밍업0·마지막판정미판정·초기head복원true·서버오류/재시도/nativecrash0·API0. pipeline3024.896초. 저장trace/MC/보상/96고정지표·공개bundle/hash·초기head#49동일/clock불변을오프라인감사통과했다(final-audit.json). 원래실패와후10미실행을고치지않는다.

PDF갱신도구의네트워크조회문제로완료전사용자가작업을전환했다. 현재PDF는이전승인전판본이며실제결과최신본으로표시하지않는다. 사용자최신지시에따라PDF보류·원목채굴초기신호판정불가유지·기존자료무결성확인→사용자예외4096학습/후10/초기복원경로를구현/개발검사한뒤background실행한다. 학습시작여부/PID는후속기록을따른다. commit/push/merge/종료없음.

## 2026-11-11 — #51 D 실제 백그라운드 시작

사용자 승인 후 **2026-11-11 17:16:23KST**, `artifacts/issue-51/real-20261111-171623/`에서 detached supervisor **PID521977**로 시작했다. 검증된source-manifest 일치·GPU/중복실행 사전확인·이전clockcertificate 사본을 보존하고, run-manifest.json에 현재미커밋소스/두설정/uv.lock/snapshotmanifest와 실제명령을 고정했다. 최초status는 **information 단계 running**이다. 이 한 번의 기동 확인 뒤에는 모델 polling을 하지 않는다.

승인된순서: 실제정보감사 → 초기10 → 종류별MC신호통과 시4096학습/32update → 후10·진단. 실제출력은 `pilot/signal/` 아래에 생성한다. 신호부족·정보감사/실행오류·미실행슬롯·server재시도/복원·시간을 보존한다. 종료이벤트가현재대화를재개하면원시결과/분모20/고정상태·2048보조·최종판정·critic/첫선택·분기·초기hash복원/비용을감사하고한국어PDF2개를갱신한다. 자식종료를blocking wait하고완료이벤트1회만보내며알림결과는completion-notification.json이다. **commit/push/merge/이슈종료·판정후연구결정은승인없이고하지않는다.**

## 2026-11-11 — #51 D 백그라운드 실행 승인·착수 준비

사용자가 D의 실제정보감사→초기10→신호통과 시4096학습→후10을 승인했다. source-manifest와 최종313pytest/54mypy의 구현이 동일한지 확인하고 별도 real-* 폴더에서 source/config/snapshot 고정·완료이벤트 방식으로 시작한다. 아직 이 기록은 준비 단계이며 실제 PID/시각/단계는 실행manifest/status와 뒤의 착수기록을 따른다. commit/push/merge/이슈종료는 별도승인전 금지다.

## 2026-11-11 — #51 A/B/C 구현·개발 검사·독립 검토 완료, D 승인 대기

**구현:** 기본false인 `pilot_signal`을 추가했다. 원목3→나무곡괭이1제작→조약돌3 고정 사슬, 개당1/N·중복/제공 제외, 현재visible 원천 블록 potential(D32/k0.3/32), 같은 상태에서 다음 목표·local return 단절을 기존 공개 실행 경로에 연결했다. #49 발견보상/기존설정은 유지하고 새파일럿에서만 끈다. MC 명시정답은 critic-only와 유한/길이를 검사하고 frozen특징을 pooling해 Choice 없이 누적32epoch로 학습한다. 최근rollout 사후EV≥0.3/최대8rollout에서 워밍업을 끝내고 기존GAE/PPO로 복귀한다.

**실행기/진단:** `mc-diamond pilot-signal --config configs/signal_pilot.yaml --output <새폴더>`와 별도 `signal/` 산출물. 초기10→종류별 MC 신호gate→LR3e-4/4096/32update→후10을 구현했다. 신호/비교표본부족은 학습0·후10미실행을 분모20에 유지한다. 초기평가 고유입력과 후보/마스크·frozen특징, update별head/확률·균등몫·엔트로피,2048보조값/4096판정,목표별완료수,첫선택분포,정책/재고·드롭시점/지도/기타 첫분기를 기록한다. 별도critic2000step 적합은 초기평가 위치·인벤토리와 겹치는 학습자료를 제외하고 livehead/RNG를 보존한다. 고정상태 지표를 온라인PPO의 미관측환경 일반화로 해석하지 않는다.

**최종 개발 검사:** 전체 **pytest313개/175.83초**, strict **mypy54파일**, diff공백검사 통과. 이전310개/139.73초는 추가전체경로/오류검사 전 기록이다. tiny모델+scripted 초기평가trace 및 공개mock RPC/PPO로4096/32/2048/33고정지표/32head/20슬롯/초기복원을 검증했다. 실제tinycritic update뒤오류주입도 전체모델hash복원·오류원문·20슬롯/후10미실행을 확인했다(정상/오류2검사38.21초). 새수치검사는1/N·제공/중복·potential부호/telescoping/대상제거·세localterminal·MC꼬리/단절·EV/상한·후보분류/마스크·고정중복·보조critic분할/RNG·분기원인을 포함한다. 실게임/공개가중치 학습 효과로 보고하지 않는다. 원시결과 artifacts/issue-51/{final-pytest.txt,final-mypy.txt,full-mock-and-fault.txt}; RED/중간결과도보존했다.

**독립 검토:** read-only 전체변경 검토와MC배치/오류검사 재검토에서 Critical/Important확정결함0. 리뷰요청의 오류복원 검사공백을 해소했다. docs/reviews/issue-51.md. #16/#17/#18/#20 인계는 docs/issue-51-handoff.md, #49LR선택을성능근거로해석하지않고 Jev요청당약US$0.0003/C4환산US$0.15를추정으로명시했다.

**실제/미실행:** E의 실제7BGPU24응답은 아래실측그대로다. **D Minecraft게임·공개NanoJev게임학습·실제정보감사·최종게임판정은 아직0/미실행**. bridge/runtime/clock.py/recipes/snapshot은변경하지않았고 기존certificate(trials63/pause_verifiedtrue/fingerprint ef3a2eda…15b3)는유지한다. 새정지인증/실제정보감사통과를주장하지않는다. 승인후백그라운드는 정보감사→pilot-signal, pinnedsource/config/snapshothash·child종료대기·완료이벤트1회를사용한다. 준비만한 artifacts/issue-51/d-supervisor-template.py는실행하지않았다.

**상태/산출물:** 작업브랜치 feat/issue-51-pilot-signal, 기준f63ed87+미커밋구현; source-manifest.json에전체Python/설정/신규검사SHA256을고정했다. **commit/push/merge/이슈종료모두미실행**. 판정후보상본학습적용/구조변경/A·B축소도자동결정하지않는다. 한국어PDF최신2개 reports/issue-051-T14B-{report,code-guide}.pdf(보고서3쪽/가이드2쪽) 생성, 한글추출·한글폰트embedding·전체5페이지렌더가독성확인. reports Git추적0·ignore확인. 생성기/중간파일은 /tmp/issue51-pdfs.py 등 /tmp에만있다. PDF때문에게임을재실행하지않았다.

## 2026-11-11 — #51 E 실제 고정 7B 확인 완료

background 정상종료/알림전송 각exit0, 전체44.537초. #49 초기평가 성공 슬롯2의 인벤토리가 달라지는 첫 상태12개에 조약돌3/다이아 과제 각1회, 총24회. Qwen/Qwen2.5-7B-Instruct revision a09a35458c702b33eeacc393d103063234e8bc28, 고정프롬프트SHA256 d3ded20bebe6c5abcbd200792963e3aa1f79aabd7429db913a5b1a8fa547806f, 실제4비트·greedy·가중치불변·GPU만 사용했다. 입력3,706–4,525토큰/합102,706, 응답지연1.120–1.743초/합29.453초. 게임/API/7B학습0.

검증통과6/24·거부18/24(전제조건16, 이미보유2). 조약돌과제는 곡괭이전9상태 모두 조약돌3을바로요구해거부, 곡괭이후3상태는유효했다. 다이아과제는9거부·3통과: 원목1개/판자4개 상태의추가원목은실행가능하나원목16개는필요량과다, 곡괭이·판자3·막대2상태의원목1개는다음단계관점에서불필요했다. 즉시실행가능한타당한선행단계5/24(수량과다1포함)이며검증통과를좋은계획으로동일시하지않는다. 원문별관측/검증/분류는 artifacts/issue-51/planner-e/{planner_probe.jsonl,classified.json,summary.json,events.jsonl}, 소스/실행hash·상태·알림도같은폴더에보존했다. #16/#17입력으로넘기며여섯조건/Astra비교를대체하거나7B학습근거로확대하지않는다.

개발기준검사는 올바른uv실행으로297pytest/138.09초통과. 첫잘못된PATH실행의144실패도아래이력에보존한다. E이후A/B/C구현중이며D게임파일럿은아직미실행/별도승인대기다.

## 2026-11-11 — #51 T14B 착수·승인값 사전 확정

E supervisor PID502415를 artifacts/issue-51/planner-e/에서 시작했고 종료 이벤트를 현재 대화로 보내도록 했다. 중간 결과 polling은 하지 않는다. 기준 개발검사의 첫 명령 `.venv/bin/python -m pytest`는 자식 CLI의 PATH에 mc-diamond가 없어144실패/153통과였으며 제품 결함으로 판정하지 않았다. `UV_CACHE_DIR=.cache/uv .tools/uv run --locked --no-sync pytest`로 환경을 바로잡아 기준 검사를 다시 시작했다(/tmp/issue51-baseline-uv-pytest.txt). 코드 변경·게임 실행은 아직 없다.

#51 본문(댓글0), #1 본문·댓글3건과 PLAN 관련 절, 2026-11-11 PROGRESS/DECISIONS를 확인했다. 사용자가 승인한 제안값·구현상 반복 횟수·최소 원목3개·return 경계·실행/승인 순서를 DECISIONS 최상단에 확정했다. E 저장 상태7B GPU 확인을 먼저 실행하고 A/B/C 구현·개발 검사를 진행한다. D 게임 파일럿은 구현/7B 결과 보고 후 별도 승인 전까지 미실행이다. push/merge/이슈 종료·판정 이후 결정도 보류한다. 기존 #49 자료는 보존한다.

## 2026-11-11 — #49 게시·PR #52 병합·종료·main 정리 완료

PR #52가2026-11-11 16:16:18KST에병합됐다(merge a96840956c57eca8fb9440d588b36ca9dd006873). #49는16:16:20KST CLOSED. 로컬main=origin/main동기화와#49게시브랜치로컬/원격삭제를확인했다. 검사된5c11c94와병합a968409의전체tree가같아검사결과가동일코드를검증한다. 원격CI체크는설정없음. 최종게시상태문서만추가로커밋/push하고원격/로컬HEAD를다시확인한다.

사용자가 현 이슈 종료·push·merge·로컬 main 동기화를 승인했다. 새 이슈는 다른 세션에서 발행하므로 만들지 않는다. 원래 게임 파일럿/보완의 실패·분모·원시자료를 보존하고 기존 미커밋 후속 trace 재검토·NanoJev 합성 보상/Jev 진단 문서도 이번 게시에 포함한다. 해당 문서의 "미커밋"은 당시 상태이며 이번 문서 커밋으로 통합한다. 새로운 게임/모델/학습/API 실행 없이 개발용 pytest/mypy와 게시 상태만 재확인한다.

종료 해석: 등록 규칙상 LR3e-4 선택(초기2/10·LR3 4/10·보완LR1 2/10)은 유효하지만 학습 효과나 LR 우월성의 증거가 아니다. trace의 비결정적 환경/표집 차이를 보존한다. 합성 보상 probe의 개선은 고정 본체 특징·Choice/PPO의 학습 가능성을 보이며 실제 게임 부진의 유일 원인까지 확정하지 않는다. Jev 30요청 비용US$0.009003708(전체 ledger누적US$0.009214842)은 두 게임pipeline API0과 별도다. 30요청으로 예산가드가멈춘 사실도 유지한다.

후속 범위: 실제 게임의 희소/지연 보상과 짧은 목표의 학습 신호, 목표·선행 단계 입력, 거의 균등한 정책/평가 비결정성, 초기 move:5 선택 편중 원인, 간헐 Java기동 지연의 근본 원인, 원목 드롭 gone/count 진단이다. 여기서는 이 문제를 해결하거나 새 이슈를 생성하지 않는다. 합성 probe·작은 표본 Jev의 해석도 후속 검토가 필요하다. #49 종료를 본 학습/7B학습/추가파일럿 승인으로 해석하지 않는다.

게시 전 최신 전체pytest297개/138.05초·엄격mypy .51파일·Node문법·diff공백검사 통과. 코드변경없이tiny/mock/fixture 개발검사만 재실행했다.

최종 원격 PR·merge SHA·#49 종료·main동기화·개발검사/PDF 검수 상태는 artifacts/issue-49/publication.json을 정본으로 남긴다. 최신 한국어PDF2개(보고서5쪽·가이드2쪽)에 실제 게시/종료·추가 진단/API비용을 반영했다. 한글추출/한글폰트embedding/전체7페이지가독성을 확인했으며reports는Git추적0이다. 생성기는/tmp/issue49-closed-pdfs.py,중간자료도/tmp에만두었다.

## 2026-11-11 — critic 기록 재검토·후속 이슈 #51 발행

**critic (오프라인, 게임·API 없음):** 파일럿 초기 critic은 모든 상태에 약 −0.72를 예측했고 실제 MC return 평균은 +0.12였다. 예측 평균은 8 update 동안 맞춰졌으나 정책 버전별 MC EV는 LR3e-4 0.04–0.24, LR1e-4는 −0.10–0.07에 머물다 마지막 두 버전에서 0.26·0.46이다. 같은 critic 구조를 저장 특징 512상태의 실제 return에 직접 맞추면 128 step에 검증 188상태 EV 0.51, 2,000 step에 0.53(LR 1e-4·1e-3 동일)이다. 같은 검증 상태에서 파일럿 critic의 EV는 초기 0.057(104상태), LR3e-4 0.076(42), LR1e-4 0.618(42)이다. critic은 연결됐으나 품질은 검증되지 않았고 실행마다 달랐다.

**중단:** 7B 계획기 하위 목표 확인(`artifacts/issue-49/probe-20261111/planner_probe.py`)은 사용자 지시로 결과 0건에서 중단했다. 첫 시도는 `validate` 인자 누락 TypeError였고 수정본은 완료 실행한 적이 없다.

**다음 작업:** 확인된 문제와 승인된 후속 작업을 [#51](https://github.com/sion0507/Minecraft_RL/issues/51) [T14B]로 발행했다. 보상 옵션 세 가지·critic 기준 워밍업·고정 상태 평가 구현, 게임 파일럿 1회, 7B 확인은 모두 미실행이며 새 세션에서 #51로 진행한다. #18·#20은 #51 판정 뒤 착수한다. #49 종료 여부와 이번 문서 변경의 커밋은 사용자 결정이다.

## 2026-11-11 — #49 후속 오프라인 진단 2건: NanoJev head는 학습됨, Jev는 목표를 그대로 따름

사용자 승인(DECISIONS 같은 날 절)으로 저장된 파일럿 상태만 사용했다. 게임 실행 0회, 실행 소스 변경 없음. 대상은 후보 설명만으로 좋은 후보가 읽히는 결정 707개(필요 블록이 적힌 이동 후보, 접근 후보와 함께 나온 채굴 후보)이며, 평가 trace의 고유 상태 188개를 검증용, 다른 위치의 학습 trace 상태 519개를 학습용으로 나눴다.

- **재현 확인:** 다시 계산한 미학습 NanoJev 확률이 초기 평가 기록 104건과 오차 0으로 일치했다.
- **진단 1 (실제 공개 NanoJev, GPU, 합성 보상):** 좋은 후보를 고르면 1, 아니면 0을 주고 기존 PPO 클래스·기본 설정·rollout 128·첫 rollout critic-only로 학습했다. 검증용 상태에서 좋은 후보에 준 확률(균등 몫 0.449, 시작 0.472)은 actor update 7회 뒤 LR1e-4 0.542, LR3e-4 0.792, LR1e-3 0.875, LR3e-3 0.814이고 117회 뒤 0.929–0.958이다. 학습용 상태의 값과 거의 같아 암기가 아니다. 보상을 좋은 후보 60%·나쁜 후보 15% 확률의 0/1로 흐리면 LR3e-4가 7회 0.601, 16회 0.820, 117회 0.889다.
- **해석:** 고정 본체 특징과 Choice head, PPO 구현과 LR은 정책을 움직이기에 충분하다. 파일럿에서 움직이지 않은 원인은 모델이 아니라 보상 신호다(에피소드 끝 보상 하나가 거의 무작위인 약 30결정에 걸림). 합성 보상은 결정마다 즉시 주어지는 가장 유리한 조건이며 실제 게임 학습 성공을 뜻하지 않는다. 학습한 head는 저장하지 않았다.
- **진단 2 (실제 Jev, 유료):** 검증용 상태 30건을 기존 JevSelector로 보냈다. 30요청 모두 200·fallback 0, 입력 4,538–8,062토큰, 확인 비용 US$0.009003708(요청당 약 US$0.0003), ledger 누적 US$0.009214842. 예산 가드(US$0.0095)가 30건에서 멈춰 예정 약 50건을 다 보내지 않았다. 곡괭이를 든 상태의 돌 방향 이동 10건은 확률 0.840(균등 0.507, NanoJev 0.491)·최고 후보 10/10, 조약돌 채굴 1건은 채굴 후보 2개에 0.79였다. 곡괭이 없이 목표가 조약돌인 15건은 원목 방향이 최고인 경우가 4건이고 원목 채굴 대 접근 4건은 접근을 골랐다. Jev는 적힌 목표를 따르며 선행 단계를 스스로 추론하지 않는다. 정규화 엔트로피는 Jev 0.78–0.88, NanoJev 0.98–0.99다. 30건 표본이며 PLAN §7.3의 A/J 진단·5분 실행은 여전히 미실행이다.
- **환산(추정):** 평가 30회 기준 1,800틱당 벽시계 208초·결정당 54.4틱·복수 후보 73%이므로 30분 에피소드는 약 69분·660결정·Jev 유료 요청 약 485회·약 US$0.15다. 조약돌 파일럿에서 환산한 값이며 실제 C4 측정이 아니다.

미실행: 7B 계획기의 저장 상태 목표 출력 확인, 짧은 목표 단위의 게임 파일럿, 본 학습. 구조 변경·추가 파일럿·7B 학습은 사용자 결정이다. 근거: `artifacts/issue-49/probe-20261111/{states.py,features.py,ppo_probe.py,ppo_probe.jsonl,ppo_probe.stdout,jev_probe.py,jev_probe.jsonl}`. 문서 변경은 미커밋이다.

## 2026-11-11 — #49 파일럿 실제 trace 재검토: 정책 선택 개선 근거 없음

사용자 요청으로 요약이 아닌 104개 attempt trace(3,046결정)를 오프라인으로 다시 읽었다. 게임·모델 추론·API 호출 0회, 실행 소스 변경 없음. 아래 "LR3e-4 선택" 절의 수치(2/10·4/10·2/10, 평균 틱)는 trace와 일치하지만 해석을 다음과 같이 보완한다.

- **평가 차이는 정책 때문이 아니다.** 평가는 슬롯마다 같은 sampling 시드를 쓴다. 초기 대비 20쌍(LR3 10·LR1 10)의 첫 분기 원인은 드롭 획득 시점 차이 7, 같은 위치의 관측 지도 차이 10(확인한 2건은 잔디·흙 random tick), 끝까지 동일 1, 같은 상태에서 다른 선택 2다. LR3의 추가 성공 2건 중 슬롯6은 드롭 시점 차이, 슬롯4는 확률 0.6%p 이내 변화로 근소한 표본이 뒤집힌 것이며 뒤집힌 선택은 설명에 stone이 없는 후보였다.
- **정책은 거의 균등 그대로다.** 같은 상태에서 후보별 확률 변화 중앙값은 LR3 0.53%p·LR1 0.32%p(최대 3.2%p·2.0%p), argmax 동일 99/111·103/106. 평가 결정의 정규화 엔트로피는 초기 0.989, LR3 0.993, LR1 0.986이다.
- **변화 방향에 일관성이 없다.** 시작 상태 확률 변화는 LR3와 LR1이 반대 방향(상관 −0.49)이다. 필요한 블록을 설명에 적은 이동 후보에 준 확률은 세 평가 모두 균등 몫과 같다(0.47 대 0.47–0.48). 돌 앞에서 Mine과 Approach가 같이 나올 때 Mine 선택은 초기 3/18, LR3 7/20, LR1 4/22다.
- **배울 신호는 있었다.** 첫 이동이 원목 쪽(move 3·5·7)이면 28/46 성공, 반대쪽(move 2·6)이면 3/25 성공이다. 이 세 후보의 확률 합은 0.353 → LR3 0.360, LR1 0.345로 그대로다.
- **10회 평가는 잡음 범위다.** 정책이 거의 같은 학습 에피소드는 34/71 성공(48%)이고 정책 버전별로 0/5에서 4/5까지 흔들린다. 2/10 대 4/10은 Fisher p=0.63이다. 학습 에피소드 첫 선택이 move:5에 23/73으로 몰린 이유(기대 9.9)는 확인하지 못했다. 전체 sampling 보정은 정상(chi2 10.7, 자유도 9)이다.

결론: 실행 연결·분모·복원 검증은 유효하나, 이 파일럿은 학습 효과와 LR 간 차이를 보여 주지 못한다. LR3e-4는 등록 규칙의 결과일 뿐 성능 근거가 아니다. 본 학습 설정에 대한 판단은 사용자 결정이다. 근거: `artifacts/issue-49/log-review-20261111/{extract.py,analyze.py,output.txt}`. 문서 변경은 미커밋이다.

## 2026-11-11 — #49 LR1e-4 보완 완료·등록 비교 및 최종 감사 완료

**실제 결과:** 원래 초기 2/10 성공·실패 포함 평균 1710.5틱, 원래 LR3e-4 후평가 4/10·1651.7틱, 보완 LR1e-4 후평가 2/10·1749.1틱이다. 등록된 성공 수 우선 규칙으로 **LR3e-4 (0.0003)**를 선택했다. 두 설정 평균 차이 97.4틱은 초기 10회에서 사전 등록한 동률 폭 202.282640547틱보다 작지만 성공 수가 달라 시간/오류 동률 판단 전에 선택된다. 원래 LR1e-4 backend_error 1건도 비교 오류 수에 보존했다. 초기 대비 LR3는 +20%p, LR1은 변화 없으며, 각각 10회의 고정 월드 파일럿으로 통계적 우월성/새 월드 일반화/본 학습 효과를 주장하지 않는다.

**분모·실패 보존:** 원래 30슬롯은 20실행·10미실행 그대로다. LR1e-4는 59결정/PPO0/세 번째 reset 기동45초 timeout 및 후평가10미실행을 유지했다. 별도 correction의 10슬롯은 모두 실행했다. 합계는 예정40 중30실행·10미실행이며 참조 초기10/LR3후10을 중복 실행으로 세지 않는다. 보완 LR1 후 실패8회와 LR3 후 실패6회는 모두 active_tick_limit이다. 보완 학습/평가 backend 오류·자연 startup timeout·native crash는 0건이다. 원래 Java 지연의 근본 원인은 미확정이다.

**학습·진단:** 보완 LR1은1024결정/8update/actor669/유효1024/무효0/미반영0, 원래LR3은1024/8/actor641이다. 각 첫128전이는 critic-only, 원래실패59전이는 폐기·미재사용이다. 시작 동일 특징에서 update0–8 확률/엔트로피를 저장했으며 LR1 최대 확률 변화0.004856·정규화 엔트로피0.997210→0.996377, LR3은0.009376·0.997210→0.998663이다. 평가 MC EV는 초기0.043719→LR1 0.332486/LR3 0.101343; 학습 MC EV는 각각−0.102003(1011전이)/−0.484373(1001전이)로 별도다. 마지막 운영 절단 전이는 MC return에서 제외했다. 학습 앞/뒤 절반 성공은 LR1 5/18→10/18(실패 포함 평균1606.61→1483.06틱), LR3 10/17→8/18(1531.76→1543.67틱)이며 고정 평가와 직접 비교하지 않는다.

**도달·발견:** 평가 곡괭이 도달 중앙값은 초기448틱(9/10), LR1 578(9/10), LR3 470(9/10). 돌 현재가시는 모두83(9/10), 첫돌채굴/조약돌획득은 초기1385(3/10), LR1 1501(4/10), LR3 1385(5/10)다. 미도달은 중앙값에서 제외하므로 검열된 비교다. 발견보상은 세 평가 모두9에피소드에서1회씩(각0.05), 총9회다. 보완 stderr의 기존 원목 드롭 gone/count mismatch 진단6건도 보존했으며 해결됐다고 표시하지 않는다.

**실제 수정 코드 인증:** pinned 구현 de4effb에서 startup→clock→information→T04→T05→pilot 모두exit0. 실제 Java/jstack 진단은 첫deadline만검증VM에서4초로줄여 dump성공→소유PID강제종료/회수→같은snapshot재복원/새Java기동/정상종료를12.835초에확인했다. 생산45초불변. rpc-errors-new.log는 이 controlled timeout/retry 각1건뿐이며 자연 간헐장애의 현장복구 검증은 아니다. 새 시계63/63·정보감사통과, T04 목재/도구/위험/드롭/빈후보/취소/복원 및 T05 furnace(철괴1/205틱)/production(철괴3/1684틱)/경계/취소/복원통과. T04 hazard/empty의CLI exit1은 기대음성검사다. 실제 controlled fixture이며 자연G2/G4를 추가하지 않았다.

**무결성·오프라인 감사:** 원래58+보완46=104개attempt trace 전체에서 후보ID/내용/순서/마스크와선택/실행/actor제외·빈reset·도달/발견/MC return/EV가요약과일치했다. 실행manifest고정 소스/설정/원래baseline hash는불변이다. 공개 best.safetensors SHA256 f68c47d66998231b86b7e91b4ed5e82ae23acf104c8b7cd6d165c3ac7b7ffe1b/revision047b927b30882a1138fc504821b82ac145a4b81a 확인, 원래/보완 initial.safetensors동일·세설정초기parameter hash동일. 양실행restored_initial=true·본체불변·학습Choice/critic변경이다. 오프라인 감사는 게임/모델추론/API를 호출하지 않았다.

**시간·비용:** 원래pipeline3시간35분17.79초(파일럿3시간5분41.81초), 보완pipeline2시간59분54.35초(파일럿2시간29분35.29초), 합산PC점유6시간35분12.14초다. 보완 사전단계는 controlled startup12.89초·clock512.26초·정보감사776.45초·T04235.68초·T05280.11초를 포함한다. 학습수집2107=사용2048+폐기59결정, PPO actor합계1310. API US$0·7B계획호출0·본학습0결정. GPU사용률적분/전력·전기료/실제GPU-hours는미측정이며PC wall time과구분한다.

**검증·리뷰·상태:** 기존 최종 개발검사 pytest297/137.04초·mypy .51파일 및 두축리뷰Standards P2 1건수정/Spec0/미해결0 기록을 유지했다. 실행소스변경이없어 이번에는 전체개발검사/게임을 재실행하지 않고 저장trace/hash/결과감사를 수행했다. 구현로컬commit de4effb, 실행전상태문서28b37d8. 최종결과문서만추가로컬commit하며 push/PR/merge/이슈종료없음. background완료/알림전송각exit0를확인했고 더이상학습/파일럿/API/자동재시도는없다.

**산출물:** 원래/보완 summary는 artifacts/issue-49/real-20261110-232814/pilot/{baseline,correction}/summary.json, 새실제검증/단계로그/RPC/알림/최종감사는 artifacts/issue-49/supplement-20261111-102747/ (final-audit.json/stdout/stderr). 감사스크립트사본도같은폴더에보존한다. 최신한국어PDF2개(보고서4쪽·가이드2쪽, 전체6쪽)는 reports/issue-049-T14A-{report,code-guide}.pdf이며 코드기준de4effb와실행코드차이·실제/mock/미실행·commit/push/merge/종료상태를분리했다. PDF한글추출/한글폰트embedding/모든페이지렌더를검수하고 reports Git추적0을확인한다. 중간자료는/tmp, 생성기는/tmp/issue49-final-pdfs.py다.

## 2026-11-11 — LR1e-4 보완 background 시작·실제 Java/jstack 복구 진단 통과

구현/실행코드 **de4effb**를 고정해2026-11-11 10:29:04KST에 `artifacts/issue-49/supplement-20261111-102747`에서 detached supervisor(PID373632)를 시작했다. 승인된새실행만수행하며원래자료는보존한다. 실제LR1e-4출력은원래pilot의독점correction/에쓸예정이다. 현재상태의정본은새background-status.json이다.

첫실제검증startup은exit0/12.835초: 실제Java기동·실제jstack출력성공·소유프로세스SIGKILL/회수·같은G1snapshot재복원/재기동성공·정상종료를확인했다. 이검증VM에서만첫기동deadline을4초로줄였고생산소스45초는그대로다. 자연기동45초지연원인을재현/해결했다고주장하지않는다. 원시startup-real.json/stdout/stderr 및 RPC timeout/retry기록을보존했다. 현재초기확인에서다음clock단계가진행중이며새실제63조건·정보감사·T04/T05후에만학습한다.

보고서/가이드PDF2개를원래실제30슬롯결과(초기2/10·LR3후4/10·LR1후10미실행)·복구코드·개발297검사/타입51파일·리뷰수정·현재보완대기상태로갱신했다. 보고서3쪽/가이드2쪽의한글추출·한글폰트embedding·전체5쪽렌더를검수했고Git추적0이다. 생성기는/tmp/issue49-followup-pdfs.py이며보고서때문에게임을재실행하지않았다. 보완완료이벤트후등록비교/진단/시간·실패회계/본체고정·복원/경험제외를최종감사하고PDF를다시갱신한다. push/merge/이슈종료/API미실행.

## 2026-11-11 — #49 기동 복구·단일 LR1e-4 보완 경로 구현/개발 검증 완료

최초 background pipeline 완료를 확인한 뒤 수정했다. Server.start에45초 timeout의 최근64KiB stdout/stderr·jstack 최대5초/1MiB 진단·소유 Java SIGKILL/최대5초 회수를 구현했다. Server.restore만 같은 snapshot을 다시 검증/복원해1회 재기동하며, 두 번째 timeout/다른 오류/진단 기록 실패/회수 실패는 중단한다. dump 부재/실패도 기록하고 정책 입력과 분리한다.

기존 correction 플래그를 통해 실패 LR1e-4 보완1회를 허용한다. 원래 config/snapshot/seed/입력·모델·가중치 및 초기heads hash를 확인하고 공개 초기값·새 optimizer에서1024결정/8update/첫critic-only와후평가10만 수행한다. 원래초기10·동률폭·완료LR3e-4결과는 재사용하고 baseline파일을 수정하지 않는다. 비교오류수에 원래LR1e-4 backend 오류도 보존한다. 이전LR3e-4가 선택 가능해도 보완학습이불능이면 command실패다.

**최종 개발 검사:** 공개 Server.restore/CLI의 RED→GREEN, 관련22검사/51.14초, stale-child 출력 회귀12검사/1.63초, 전체 **pytest297개/137.04초**, strict **mypy .51파일**, Node 문법/diff 검사 통과. 최초전체296개/137.51초는 리뷰 수정 전 근거다. 원시 `artifacts/issue-49/{startup-red,supplement-red,supplement-green,recovery-targeted,recovery-review-red,recovery-review-green,recovery-full-pytest-final,recovery-mypy}.txt`.

**리뷰:** Standards P2 1건(종료된 Java의 늦은 Done이 새 Java를 준비 완료로 오인)을 재현·수정했다. 현재 child 출력만 전달하도록 하여 RED freshReady=false→GREEN을 확인했고 전체 재검사했다. Spec0·미해결0. `docs/reviews/issue-49-startup-recovery.md`.

**실제 검증/실행:** 수정 코드의 새 실제 Java 진단·63조건 인증·정보감사·T04/T05 및 보완학습은 다음 pinned background chain에서 순차 수행하며 현재 개발 검사만으로 실제 성공을 주장하지 않는다. 이 별도 진단 VM은 첫 기동 deadline만4초로 줄여 실제 jstack/kill/restart 경로를 확인하며 생산 코드45초는 바꾸지 않는다. 모든 사전 단계 통과 후에만 보완학습을 시작한다. 코드·명령·원래baseline/hash·이전/새fingerprint·RPC오류/전체시간을 보존하고 완료이벤트로 결과감사를 재개한다. push/merge/이슈종료/API 미실행.

## 2026-11-11 — #49 최초 실제 캠페인 종료·보완 실행 착수

종료 이벤트가 실제로 같은 대화를 재개했다. `real-20261110-232814` pipeline은3시간35분17.79초, 파일럿 단계3시간5분41.81초에 종료(exit0). 사전 시계63/63·정보감사·T04/T05 회귀 통과. 정상 종료와 모든 설정의 완주를 구분한다.

- 초기평가 **2/10**, 실패포함 평균1710.5틱. 등록된 시간동률폭202.282640547틱.
- LR1e-4: **59/1024결정·PPO0**, third reset 서버 기동45초 timeout으로 불능. 미업데이트59전이, 후평가 **10슬롯 미실행**을 원래30슬롯 분모에 유지한다.
- LR3e-4: **1024/1024결정·PPO8회·actor641**, 유효전이1024/무효0, 본체불변·Choice/critic변경. 후평가 **4/10**, 실패포함 평균1651.7틱. 초기대비 성공2회 증가지만 짧은10회 결과이며 학습 효과의 통계적 우월성을 확정하지 않는다. 시작확률 최대변화0.009376, 정규화엔트로피0.997210→0.998664. 평가 MC critic EV0.043719→0.101343; 학습 MC EV는−0.484373로 별도 지표다. 학습 앞17에피소드10성공/뒤18에피소드8성공은 고정 평가가 아니다.
- 원래30슬롯 중20실행/10미실행. 코드 selected_choice_lr=3e-4는 유일하게 usable한 설정의 임시 선택이며 두 설정 비교 완료가 아니다. 공개 초기heads 복원true, 추가 본 학습0·API US$0. 돌/원목 드롭 병합 관련 진단은 stderr에 남아 있으며 성공·실패로 조용히 덮지 않는다.

앞서 승인된 순서에 따라 timeout 진단/1회 재기동 패치를 구현·검증한 뒤 LR1e-4만 공개 초기 상태에서 보완 실행한다. 원래 기록은 수정하지 않는다. 실행계획 docs/superpowers/plans/2026-11-11-issue-49-startup-recovery.md. 완료 이벤트의 이전 재실행 금지 문구보다 사용자의 후속 명시 승인/CONTEXT 최상단을 따른다.

## 2026-11-11 — timeout 패치 후 실패 LR1e-4 재실행과 최종 검토 승인

사용자가 현재 백그라운드 실행 종료 알림 후 패치를 적용하고 실패한 LR1e-4도 다시 실행한 뒤 원래 예정한 검토·검증을 마무리하라고 지시했다. 이전 LR1e-4 자동 재실행 금지를 이 보완 실행1회에 한해 대체한다. 현재 실행 소스는 그대로 두고 종료 후 구현/검증 → 새 시계 인증·정보감사·회귀 → 공개 초기 상태에서 LR1e-4 1024결정/8update·후평가 → 등록한 비교/진단/복원/비용 감사·최신PDF2개 순서로 진행한다. 원래 실패59결정·미실행 슬롯과 LR3e-4 결과를 보존하고 별도 경로/코드 기준으로 보완한다. CONTEXT·DECISIONS와 after-pilot-action.json에 최신 승인을 기록했다. 실제 패치/보완 학습은 아직 미실행이며 현재 캠페인 종료를 기다린다.

## 2026-11-11 — 파일럿 진행 중 서버 기동 timeout 원인 확인·종료 후 수정 승인

현재 artifacts/issue-49/real-20261110-232814 실행의 사전 검증(시계63/63·정보감사·T04/T05)은 모두 통과했다. 초기평가2/10성공. LR1e-4는59/1024결정·PPO0에서 세 번째 reset이 실패했다. 서버 rpc-errors.log의 직접 원인은 `Server startup timeout`(bridge/server.js:81,45000ms), 오류 로그 마지막 쓰기는00:42:47, 실패 attempt 전체55.35초·활성틱/결정0이다. 당시 Java 상세 기동 로그는 현재 보관분에 없고, 동시간대 kernel 로그에 OOM/segfault 근거는 없었다. 원시 오류 사본·진단 JSON·최근 정상8회 기동 첫로그→Done 평균6.375초(6–7초)는 같은 실행 폴더에 보존했다. 근본 지연 원인은 미확정이다.

사용자가 **파일럿 종료 후** 최근 Java 출력+jstack 진단과 강제종료 후1회 재기동을 승인했다. 적용 범위/기존 중단 규칙의 한정 예외는 DECISIONS 최신 절에 기록했다. 현재 실행 소스는 변경하지 않고 후속 작업을 CONTEXT 및 after-pilot-action.json에 남긴다. 완료 이벤트가 오면 현재 결과 보존·보고 후 구현을 이어간다. 현재 실패 설정을 재실행하거나 새 파일럿을 자동 추가하지 않는다.

## 2026-11-10 — #49 mypy 검사 범위 정리·실제 백그라운드 실행 승인

사용자가 artifacts 제외와 실제 파일럿 실행 및 종료 이벤트 기반 결과 보고를 승인했다. `mypy .`는 artifacts 보관 소스/외부 checkpoints 코드를 제외하고 진단 도구의 타입 표기2곳을 정리한 뒤 **50파일 통과**했다. 실행 계산은 불변이며 전체pytest286개 결과를 유지한다. 이 변경으로 실제 게임을 타입 검사에 사용하지 않았다.

호스트의 Codex CLI/daemon0.167.0이 실행 중이고 `codex queue --resume`을 지원함을 확인했다. GPU RTX5070Ti16GB 사용967MiB, 중복 Minecraft Java/학습 프로세스 없음. 백그라운드 실행은 사전 검증과 파일럿의 child 종료를 기다렸다가 같은 대화에 완료/실패 이벤트를 보내도록 준비했다. 실제 PID·단계·결과는 `artifacts/issue-49/real-*/background-status.json`, 코드/hash·명령은 run-manifest.json, 알림 전송 결과는 completion-notification.json을 따른다.

실제 순서: 시계63조건 → 정보감사 → T04 macros → T05 furnace/production/boundaries → #49 pilot. 어느 단계든 실패하면 이후를 실행하지 않고 통지한다. 중간 모델 polling·자동 재시도·새 자연G2/G4/API/추가 파일럿은 없다. 초기10평가가2–8성공을 벗어나도 기존 gate에서 멈춘다. 성공·실패·미실행과30슬롯 분모·native crash/미복원을 구분해 종료 후 결과와 최신PDF2개를 보고한다. 이전 아래의 실제 보류 문구는 이 사용자 승인 이전 이력이다. push·merge·이슈 종료는 미실행이다.

## 2026-11-10 — #49 구현·개발 검사·리뷰 완료, 실제 파일럿 보류

사용자 `$implement` 요청과 도착점 중심 16블록/현재 가시성 수정 승인으로 현재 main `a5ef033`에서 구현한다. #49 본문의 이동 설명을 합의한 문구로 수정했다. 세 기능(파일럿 발견 보상 0.05·1,800틱·공통 이동 설명), 초기 표본 SD 기반 동률 폭 사전 기록과 확률/엔트로피·학습 절반·MC EV·도달 틱/발견 횟수 진단을 구현했다. 세부 선택은 DECISIONS 같은 날 #49 절을 따른다.

**실제 실행:** 사용자 지시로 Minecraft/공개 모델 파일럿·학습·평가·API 호출 0회. 실제 63조건 시계 인증·정보 감사·물리 회귀도 미실행이다. bridge 파일 변경으로 기존 인증을 새 코드에 승계하지 않는다. #49의 실제 수락 검증·설정 선택과 이슈 종료는 미완료다. 기존 #15 산출물과 실패 이력을 보존한다.

**개발 검사:** 최종 전체 **pytest 286개/120.46초**, 엄격 **mypy src/tests 40파일**, Node 문법·diff 공백 검사 통과. `mypy .`는 기존 `artifacts/issue-15/loaded-source/src/mc_diamond/cli.py`의 상대 import 오류로 exit2이며 통과가 아니다. 수치/공개 CLI/Node VM 계약을 RED→GREEN으로 확인했고, 평가·학습 개발 검사는 tiny 모델과 scripted mock만 사용했다. 원시 근거 `artifacts/issue-49/{targeted-tests,full-pytest-final,mypy,mypy-dot,review-red,review-green}.txt`.

**두 축 리뷰:** Standards P2 1건(terminal 전이 후 최종 검증 실패 attempt가 학습 MC EV에 포함)을 공개 CLI 회귀로 재현했다. RED 32전이/EV값 → valid attempt 필터 수정 후 GREEN 0전이/null EV. 수정 후 전체 검사를 다시 통과했다. Spec 0건, 미해결 0건. 상세 `docs/reviews/issue-49.md`. 초기 전체285개/118.69초는 수정 전 근거로 별도 보존한다.

**상태:** 현재 main 로컬 커밋으로 전달하며 push·merge·이슈 종료는 미실행이다. #49는 OPEN이고 합의된 16블록/현재가시성 본문 게시를 다시 확인했다. 한국어 로컬 산출물은 `reports/issue-049-T14A-{report,code-guide}.pdf` 두 개이며 코드 기준은 PDF에 최종 commit SHA로 고정한다. 보고서 때문에 게임을 재실행하지 않는다. 실제 파일럿·새 시계 인증·정보 감사는 사용자의 별도 실행 지시까지 시작하지 않는다.

**PDF 검수:** 구현·검증 보고서 2쪽, 코드 가이드 2쪽의 한글 추출·한글 글꼴 embedding·전체 페이지 렌더 가독성을 확인했다. 생성기는 `/tmp/issue49-pdfs.py`, 중간 text/PNG도 `/tmp`에만 두며 reports에는 최신 PDF2개만 추가한다. 최종 코드 commit 후 같은 생성기로 SHA를 고정해 갱신한다. reports Git 추적0을 확인한다.

## 2026-11-10 — #15 돌 3개 파일럿: LR 1e-4 완료, LR 3e-4 학습 중 segfault로 미완료

`pilot-wood --config configs/wood_pilot.yaml --output artifacts/issue-15/stone` 실제 실행(13:52~17:57, exit 139). 근거: `artifacts/issue-15/stone.stdout`, `stone.stderr`, `stone.exit`, `stone/baseline/`.

**실제 결과:** 초기 평가 8/10 성공(실패=3,600틱 포함 평균 2,383틱), 난이도 gate 통과. LR 1e-4는 1,024결정·update 8회(첫 update critic-only, actor 전이 668) 후 평가 8/10 성공·평균 2,147틱. 차이 236틱은 등록한 동률 폭 750틱 미만이라 개선으로 판정하지 않는다. 학습 에피소드는 온전한 24회 중 19회 성공(앞 12회 9, 뒤 12회 10). 본체 hash 불변, Choice·critic hash 변경.

**오프라인 진단(저장 trace만 사용, 게임 미실행):** 시작 상태 8후보 확률은 초기→LR 1e-4 후 최대 0.005 변화(예: 0.151→0.146), 정규화 엔트로피 0.988→0.988로 정책이 사실상 움직이지 않았다. 평가는 슬롯별 표집 난수가 같아 초기·학습 후 첫 선택 10개가 모두 일치하고 3개 슬롯은 궤적 전체가 같다. MC return 기준 local critic EV는 초기 0.08(V 평균 −0.74, return 평균 0.57) → 학습 후 평가 0.35(V 평균 0.35, RMSE 1.35→0.39). 곡괭이 도달 중앙값은 초기 542틱·학습 후 517틱. 실패는 대부분 move 후보만 반복하다 시간 소진(곡괭이 제작 뒤 돌 미발견 또는 나무 발견 지연)이다.

**실패:** LR 3e-4 학습 7번째 에피소드 중 17:57:08 Python 프로세스가 native segfault(kernel: `mc-diamond[79345]: segfault at 0 ip 0`)로 종료했다. Python traceback·core 없음, 원인 미확인. 완료된 6 에피소드(4성공·2시간소진)의 update 통계는 stdout에 남지 않았다. LR 3e-4 후평가 10슬롯·설정 선택은 미실행이다. 재실행은 사용자 승인 전 하지 않는다.

**다음 작업:** #15는 이 결과로 종료했다(사용자 결정). 발견 보상·1,800틱 예산·이동 후보 설명 보강을 넣은 두 설정 재실행과 설정 선택은 #49에서 새 세션으로 진행한다. 이 세션의 코드 변경(돌 3개 과제, critic 워밍업, 분리 클리핑)은 미커밋 상태다.

## 2026-11-10 — #15 사용자 요청으로 실제 파일럿 중단 / 학습 연결 확인·성능 효과 미검증

사용자가 "일단 멈춰봐 여기까지 하고 그리고 실제로 의미가 있었나 말해봐"라고 지시했다. 실제 CLI에 중단 신호를 보내 exit130으로 종료했다. host process 조회에서 학습/Minecraft Java 프로세스가 없고, nvidia-smi compute 목록에서 해당 Python 모델이 사라져 GPU 메모리 반환을 확인했다. 추가 게임/모델/학습/API를 실행하지 않는다. 아래 진행 중 기록은 중단 전 이력이다.

**실제 근거(약98.4분):** 초기 고정 평가10회 중9성공·1활성시간소진. 첫 LR1e-4에서619선택/619실행 결정을 수집했다. 완전128전이 update4회로512유효전이(유효 actor108+111+113+115=447개)를 PPO에 사용했다. Choice/critic은 네 번 모두 변했고 최초 ratio는 모두1, Choice/전체 gradient는 유한했다. 학습 중 완료43에피소드 중42회 원목 목표 달성·직접 원목174개를 기록했다. 이 수치는 정책이 변하는 학습 기록이며 초기/학습 후 고정 평가와 직접 비교하지 않는다. 원목4 고정 목표·7B미호출·실제 정지 인증을 유지했다.

**미완료:** 첫 설정619/1024·4/8update, 두 번째 LR3e-4 미착수, 두 설정 후평가20슬롯 미실행, 설정 선택 보류(사용자 중단). 수집107결정은 PPO 미반영이며 마지막 pending/중간 episode를 포함한다. 본 학습0결정·API US$0이다. 코드 구현과 실제 학습 연결 검증에는 의미가 있었지만 성능 향상·LR우열·본 학습 준비 완료의 증거는 없다. #15 전체 실제 검증/이슈 완료로 표시하지 않는다.

**복원/재개 한계:** 중단 unwind 중 initial heads load도 KeyboardInterrupt로 끝났다. 실행 중 객체의 초기 복원 hash·본체 최종 hash 비교는 미확인이다. 디스크 best.safetensors의 공개 고정 SHA-256 f68c47d66998231b86b7e91b4ed5e82ae23acf104c8b7cd6d165c3ac7b7ffe1b는 일치한다. 원본은 변경되지 않았고 중간 학습 actor/optimizer/RNG checkpoint는 없다. 현재 구현은 이 지점의 정확한 checkpoint 재개를 제공하지 않는다. 원시 로그·초기 heads·네 update는 보존한다. 원시 episode actor 요약은 누적값이므로 합산하지 않고 transition/PPO 필드로 집계했다.

**소프트웨어 상태:** 구현f8f3894·요약 집계 수정e3b0b9d를 현재 main에 로컬 커밋했다. 최종 pytest271개/124.26초·strict mypy src/tests38파일 통과, 두 축 리뷰 미해결0/0. mypy .는 기존 Git 제외 pathfinder artifacts의 중복 analyze.py로 exit2다. push/PR/merge/이슈 종료는 수행하지 않았다.

**증거:** artifacts/issue-15/stop-summary.json은 사용자 중단 뒤 보존된 원시 로그에서 재구성한 별도 중단 요약이다. 정상 종료 baseline/summary.json은 생성되지 않았다. real.stdout/stderr·real/baseline/*.jsonl.gz·real-loaded-code.json·loaded-source와 검사/리뷰 자료를 보존한다. reports의 이 티켓 최신 구현/검증 보고서와 코드 가이드 PDF2개는 중단 상태·한계를 구분하며 보고서 때문에 게임을 재실행하지 않는다. 파일은 reports/issue-015-T14-report.pdf(2쪽)와 issue-015-T14-code-guide.pdf(2쪽)다. 코드 가이드는 e3b0b9da89b91d9d6fea5379513d0ae59622f6a1의 AST 시작 줄을 사용한다. 한글 추출·대체문자 없음, 사용한 한글 TrueType 글꼴의 embedded/subset/Unicode mapping, 1500px 렌더4페이지 전체 가독성을 확인했다. 중간 파일은 /tmp에만 있고 reports는 Git 추적0이다.

## 2026-11-10 — #15 T14 구현·리뷰 수정 완료 / 실제 파일럿 진행 중

사용자 `$implement`에 따라 main `f48ccf1`에서 구현했다. `pilot-wood`는 고정 원목4 목표를 NanoJev에 전달하고, 동일 공개 초기 heads·난수에서 Choice LR 두 값만 바꾼다. 에피소드 경계를 넘어128결정 rollout을 모으며 각 설정1,024결정/8update, 공통 초기10+후10×2평가를 연결했다. baseline/correction 독점 생성과 추가 파일럿 최대1회, 평가 예정 분모·서버 오류1회 재시도·실패 경험/시간·초기heads복원을 구현했다. 결정은 DECISIONS 최신 #15 절, 계획은 docs/superpowers/plans/2026-11-10-issue-15-wood-pilot.md다.

- **개발 검사:** 최초 전체269개 통과(123.19초). 독립 리뷰2축에서 부분 에피소드 오류 회계와 선택적 의존성 import 안내를 수정하고 각각 RED→GREEN을 확인했다. 0의 corrective LR이 default로 바뀌던 입력 처리도 RED→GREEN으로 수정했다. 최종 pilot11개/40.11초, mypy src/tests38파일 통과. 리뷰 수정 후 최종 전체 **pytest271개/126.46초** 통과(artifacts/issue-15/full-pytest-final.txt).
- **에피소드 집계 후속 수정:** learner를 episode 간 공유하면서 기존 EpisodeSummary.actor_transitions가 누적값을 반복 보고했다. 공개 CLI 합계 비교에서 RED16,896vs1,024를 확인하고 reset 전/후 기준값과 종료값의 차이로 수정했다. 관련27개/39.02초·strict mypy38파일·최종 전체 **pytest271개/124.26초** 통과. 같은 리뷰어 재검토0/0. 실제 진행 중인 원시 episode 요약은 이전 누적값이므로 합산하지 않고 transition.actor_valid와 setting 합계를 대조한다. 정책·보상·PPO 연산에는 영향이 없다.
- **리뷰:** Standards 최초P2 2건, Spec 최초P2 1건(회계 누락 중복); 같은 리뷰어들의 수정 재검토에서 미해결0/0. docs/reviews/issue-15.md.
- **실제 실행:** 승인된 GPU/로컬 서버 명령이 artifacts/issue-15/real에서 실행 중이다. 자연 G1의 고정 snapshot manifest hash `72734522fb22eb506c72dd1fbd2df560cc2f4192ebf16d3047dd2bae77f64d89`, 제공재고0, 학습seed11015·평가15000–15009. 현재 초기 평가의 실제 원목4·정지 인증 통과를 확인했으나 전체30슬롯·2,048학습결정은 아직 진행 중이다. 최종 요약 전 성공률/학습 완료를 확정하지 않는다. 원시 *.jsonl.gz, real.stdout/stderr, baseline/summary.json을 따른다. 실제 실행은 리뷰 전 로드된 소스를 유지하며 회계 오류/의존성 guard 수정은 정상 경로에 영향을 주지 않는다. 런타임 소스 hash는 real-loaded-code.json에 기록했다.
- **타입 검사 범위:** mypy .는 기존 Git 제외 artifacts의 pathfinder 두 analyze.py 중복 모듈로 exit2다(mypy-dot.txt). strict mypy src tests 통과와 구분한다.
- **미실행:** 교정 추가 파일럿, 본 학습30,000결정, #16 G4/AJ 진단, 커리큘럼/복구/lock/최종 평가, 7B 학습·Jev/Astra/API 호출0. 보고서 때문에 게임을 재실행하지 않는다. push/PR/merge/이슈 종료는 하지 않는다. 코드 커밋·PDF2개와 최종 실제 결과는 완료 절에서 기록한다.

## 2026-11-10 — #14 게시·병합·종료 승인 / 원격 #12 통합

사용자가 #14의 push·PR 병합·이슈 종료를 승인했다. 원격 main은 #12 PR #47(`a48253a`)이 앞서 있어 feat/issue-14-ppo에서 보존 merge했다(`cb29ca5`). 충돌한 CLI/schema는 smoke-ppo/smoke-jev·PPO/Jev 두 설정을 모두 유지하고, DECISIONS/PROGRESS의 양쪽 이력도 보존했다. 보고서와 이번 검증에서 #12의 유료 API를 호출하지 않는다.

통합본 개발 검사 원시: `artifacts/issue-14/publication-{pytest,mypy,targeted-uv}.txt`. 처음 `.venv/bin/python -m pytest`로 직접 실행한 일부 CLI 검사는 PATH에 mc-diamond가 없어16개 실패/25개 통과였다(`publication-targeted.txt`). 원인은 설치 부재가 아닌 uv 실행 환경을 거치지 않은 명령이며, 저장소의 uv run 명령으로 다시 확인한다. 전체 suite도 uv run으로 실행한다. 최종 결과는 아래 게시 전 검사 기록에 추가한다.

게시 전 최종 확인: 통합본 전체 **pytest260개/90.39초**, 관련41개/12.79초, strict mypy src/tests36파일 및 diff 검사 통과. .github workflow는 없어 이 결과를 원격 CI 통과로 표시하지 않는다.

실제 게임/모델/유료 API는 게시 때문에 재실행하지 않는다. 최종 push·PR·원격 main merge·#14 종료 상태와 SHA는 `artifacts/issue-14/publication.json`, GitHub PR/#14 및 최신 PDF2개에 남긴다. 아래 미푸시/Open 표시는 승인 전 이력이다.

## 2026-11-10 — #14 T13 최종 검증·리뷰 수정·로컬 커밋 완료

**코드 기준:** 구현 `7630857`, 리뷰 수정 `34dd151`(main 로컬). 최초 구현/검증 과정은 아래 같은 날 절에 보존한다. push·PR·원격 merge·이슈 종료는 하지 않았다.

**최종 개발 검사:** learning16개/2.59초, 전체 **pytest250개/82.83초**, strict **mypy src/tests34파일** 통과, diff 공백 검사 통과. 원시 `artifacts/issue-14/{targeted-tests,full-pytest-final,mypy}.txt`. `mypy .`의 기존 pathfinder artifacts 중복 모듈 exit2는 앞선 기록대로 유지한다.

**독립 리뷰:** code-review의 Standards0, Spec P1 1건을 수정했다. 실제 bridge는 사망에서 stable_boundary=false이므로 이를 무조건 요구하면 사망 -1/-20이 actor/critic에서 사라졌다. 공개 CLI local/full 사망2검사를 RED로 재현한 뒤, 신뢰할 수 있는 task terminal은 안전 지면 없이도 학습하고 bootstrap0을 유지하도록 수정했다. 같은 Spec 에이전트의 재검토에서 기존 P1 해결·새 material 지적0을 확인했다. `docs/reviews/issue-14-T13-2026-11-10.md`에 두 축을 분리해 남겼다.

**검증 범위:** 실제 공개 NanoJev+mock 게임2전이/1update와 기존 실제 로그5개 offline 재생은 아래 기록을 따른다. 공개 모델 진단은 정상 local 경로에서 수행했고, 다이아/사망 분기 수정 뒤 새 GPU·게임 진단은 하지 않았다. 해당 수정은 공개 수치/CLI 검사·기존 실제 로그와 최종 전체 회귀로 확인했다. 새 실제 게임 PPO·물리·파일럿·본 학습·처리량/예산/lock·외부 API를 검증했다고 표시하지 않는다. 사건별 발생 틱은 RPC에 없어 sparse 보상은 반환 경계 마지막 틱이다.

**보고서:** `reports/issue-014-T13-report.pdf`(2쪽), `reports/issue-014-T13-code-guide.pdf`(3쪽). 코드 가이드는 `34dd151a4add14e48028d5df8951482b1afbc153`과 AST 시작 줄을 기준으로 한다. 한글 추출·대체문자 없음, 사용한 한글 TrueType 글꼴의 embedded/subset/Unicode mapping과 1500px 렌더5페이지 전체 가독성을 확인했다. reports는 Git 제외/추적0이며 이 티켓 PDF2개만 두었다. 중간 생성기·텍스트·PNG는 /tmp에만 있다. 보고서 때문에 모델/게임을 재실행하지 않았다. `artifacts/issue-14/evidence.json`에 코드 SHA-256·검사/모델 근거를 보존했다.

**다음:** #15 목재 파일럿과 #18 커리큘럼이 사용할 학습 기반을 구현했다. #12 Jev는 별도 착수 가능하다. 실제 게임의 사건/목표/보상 전체 연결은 #15/#16, 복구는 #19, 실제 처리량·예산/lock은 #20에서 검증한다.

## 2026-11-10 — #14 T13 보상·시간 할인 PPO 연결 (리뷰 전)

**구현:** 사용자 implement 요청으로 main `b0d239a`에서 시작했다. RewardLedger(local/full·제공 제외·진행18·의미 목표8회/4), 실제 틱 할인·저장 State/Transition·GAE/PPO와 공통 run_episode의 학습 연결, 공개 `smoke-ppo`를 추가했다. Choice/독립 critic만 학습하고 본체/관측/bridge/runtime/snapshot은 바꾸지 않았다. sparse 사건은 현재 RPC의 반환 경계 마지막 틱에 배정하며 원시 사건 시각으로 표시하지 않는다(DECISIONS 같은 날 절).

**개발 검사:** 새 learning 검사14개 통과(2.35초), strict mypy src/tests34파일 통과. 최초 전체 pytest248개/82.90초 통과 후 드롭 좌표 계약을 수정했다. 수정본 최종 전체 회귀와 code-review 두 축은 다음 완료 기록에 남긴다. `mypy .`는 기존 Git 제외 artifacts의 pathfinder 두 analyze.py 중복으로 exit2이며 통과로 표시하지 않는다. 결과 파일은 `artifacts/issue-14/{targeted-tests,mypy,mypy-dot,full-pytest}.txt`다.

**실제 공개 모델 + mock 게임:** `public-model-mock-final.jsonl` exit0. 공개 NanoJev revision/초기 weight hash는 #11과 동일하다. 저장된 두 복수 후보 결정·40mock틱·보상합0.96·PPO1회/4epoch, 최초 ratio [1,1], trace [true,false]. 정책 손실 [0,0.00071451,0.00077176,0.00069207], 유한 gradient norm, Choice/critic 변경·본체 hash불변, 전체 약11.74초. 결과 actor는 저장하지 않았다. 원목 획득은 scripted mock 사건이며 실제 Minecraft 성능이 아니다. 실행은 full 다이아 드롭 좌표 수정 전이며 해당 local 원목 경로는 수정하지 않았다. 첫 단일 전이 진단도 보존했다(정규화 advantage0, actor는 entropy 경로); 최종 두 전이 결과와 혼동하지 않는다. 첫 uv 시도는 sandbox 밖 캐시 쓰기 때문에 exit2, 승인 후 실행했다. 유료 API0·본 학습0이다.

**기존 실제 로그 재생(새 게임 실행 아님):** #44 원시 G1(3step), 제작(54), G3(15), 자연 G4(63), 지급 다이아(2)를 새 ledger로 재생했다. local G1/G3/G4 성공+1, 제작 직접 진행18·목표0.5, 지급 다이아 성공 보상0을 확인했다. 드롭의 비정수 생성 좌표를 블록 좌표와 같다고 보던 결함을 RED→GREEN으로 수정했다. `previous-real-log-replay.json`에 출처와 구성별 합계를 남겼다. 새 게임/모델과의 전체 연결 검증으로 주장하지 않는다.

**미실행/후속:** 실제 Minecraft PPO·새 63조건/정보 감사(bridge 변경 없음)·실제 모델 full 학습·파일럿·30,000결정 본 학습·커리큘럼/복구/lock·최종 C4/G4·Jev/Astra·7B 학습은 미실행이다. 실제 사건/보상 전체 연결은 #15/#16, 예산은 #20에서 확인한다. push/PR/원격 merge/이슈 종료는 요청되지 않았다. 로컬 PDF2개와 최종 커밋/리뷰 결과는 완료 기록에서 제공한다.

## 2026-11-10 — #12(T11) Jev 실제 연결·선택 모드·비용 ledger

브랜치 `issue-12-t11`(main `b0d239a`에서 worktree). 결정은 DECISIONS 2026-11-10 두 절. 원시 기록은 worktree의 `artifacts/issue-12/real-{1,2}/`(Git 제외). 사용자 승인 상한 US$10 안에서 실제 호출했다.

**개발 검사:** pytest 244 통과(새 `tests/test_jev.py` 8건 + 평가 2건: Jev 불가 시 A/B 실행·J/F 미실행 분모 유지, ledger 이어 세기), `mypy src tests` 33파일 통과. 모의 API로 key 매핑·mask 제외·같은 입력 1회 재요청→fallback·통신 재시도 상한/대기·401 키 제거·상한 초과 시 미전송·불완전 분포의 native 분류·후보 1개 무요청을 검사했다.

**실제 Jev (2026-11-10, mock Minecraft):**

|실행|결과|
|---|---|
|`smoke-jev` native_choice (real-1)|exit 0. 요청 `typesafe/jev-1.13` → 응답 모델 `typesafe/jev-1.13-20260917`, 제공처 TypeSafe. 후보 2개, `probabilities` {a0 0.69, a1 0.31}(합1), choice=a0=argmax, confidence 0.38(분포와 다른 값). 입력 751·출력 34토큰, US$0.000031542|
|분포 확인 5회 (3후보 동일 입력)|모두 완전·합1, choice=argmax(a0 0.81–0.83 / a1 0.16–0.18 / a2 0.01). 요청당 US$0.00002961. 응답이 거의 결정적이다|
|`smoke-jev` sampling (real-2)|exit 0, `selector_mode=sampling`, 확률을 candidate_id로 기록, fallback 0|

- **과금:** 확인 비용 = 입력 토큰 × US$0.042/100만, 출력 US$0(751토큰 → 0.000031542, 정확히 일치). ledger 누적 7요청 **US$0.000211134**(미확인 0). 계정 `/api/v1/key` 사용량은 마지막 요청 직후 0.000179592로 앞 6요청 합과 같다(계정 반영 지연 1건). 키 한도 US$10.
- **추정(측정 아님):** 실제 C4 결정의 입력은 계획기 기준 약 3,700토큰 상태 + 후보 16개라 요청당 약 6–8천 토큰, 약 US$0.0003으로 본다. J/F 10회×수백 결정이면 약 US$1 수준이다. 실제 요청당 토큰은 T13/T14의 실제 게임 진단에서 잰다.
- **미실행:** 실제 Minecraft 위 Jev, A/J 6상태 진단·5분 실행(Task 9), Astra 호출(별도 승인 필요), J/F 슬롯의 실제 선택기·슬롯 시드 연결(T19/T22).

## 2026-11-09 — #44 관측 반경32·공통 256칸 요약 구현과 실제 검증

브랜치 `feat/issue-44-observation`(main `e9e84ae`에서 시작, push 안 함). 커밋은 `b7c0787`(구현), `bf19d8a`(리뷰 반영: 호출별 요약 누락 기록·드문 종류 보장), `e335130`(검사기 단언·문서), `47a9a9e`(원목 후보 결함)다. 결정·사전 등록·실행 중 변경은 DECISIONS 최신 #44 절. 원시 `artifacts/issue-44/real-1/`(Git 제외).

**개발 검사:** 최종 pytest 234 통과, `mypy src tests` 31파일 통과. 반경8 결과는 합성 평지·동굴·터널 각 2위치에서 이전 코드와 칸·순서까지 같다(CPU 합성). 반경32 대각선 54걸음 광선 도달 테스트는 이전 상한32를 넣으면 실패한다(RED 확인).

**실제 Minecraft(bridge fingerprint `bc7a012d…e5bc`, 모든 실행 `pause_verified=true`; bridge는 `b7c0787` 이후 바뀌지 않음):**

|검사|결과|
|---|---|
|63조건 시계 인증|**63/63 통과**, 새 fingerprint 인증서|
|정보 감사|**통과**, 23범위. 벽 뒤 광석/용암만 다른 쌍의 노출 전 정책 입력 hash 동일(지도 18,357칸·후보 8), 노출 뒤에만 다름|
|T07 tunnel·계단 장면·다이아/철 fixture|통과. 첫 실행은 검사기 단언(지도 칸 수 증가)이 공기 창과 맞지 않아 멈춤 → 단언을 "파낸 칸이 열린 칸으로 관측"으로 바꿔 남은 검사 재실행(DECISIONS 22:15)|
|자연 G4|**다이아 직접 채굴·획득**(관리자 검증 다이아1·철3), 63결정·4,149틱(반경8 #9: 63결정·3,902틱). 관측 광석 철14·석탄18·레드스톤2·청금석2·다이아2|
|자연 G2|철 0, `active_tick_limit` 12,000틱·168결정(반경8 #9: 195결정, 철 0). 성공 필수 아님, 기록만|
|T06 계단·자연 G3|1차는 장면 준비 중 Minecraft 서버 종료(`Server exited during command`/startup timeout, 서버 로그는 이후 회전으로 소실)로 중단 → 서버 오류 1회 재실행 통과. 자연 G3 15결정·2,440틱(#9와 같음)|
|T05 생산·경계|통과, 54결정·1,770틱(#9: 54결정·1,806틱)|
|T04 매크로|통과(wood_hazard·empty exit1은 #9와 같은 예상 결과). 원목 결함 수정 뒤 재실행도 통과, wood_hazard는 이번에 원목 획득(exit0)|
|자연 G1 고정 선택기(수정 뒤)|원목 1 직접 획득, 3결정·221틱|

**시작 관측(시계 미인증 진단, 같은 snapshot):**
- C4/G1/G2/G3 지표면 시작: 정책 지도 22,885칸(공기 20,755·비공기 2,130), 프레임 2.49MB, observe 왕복 0.19–0.26초, 처음 관측한 열린 칸 56,468. 원목 12개가 보인다(반경8에서는 0).
- **G4 시작: 반경32에서도 다이아·광석이 보이지 않는다**(막힌 갱도, 320칸·비공기 176). 시작 즉시 노출로 인한 난이도 하락은 없다. snapshot·시작점은 바꾸지 않았다.
- wait 20틱 step 2.66–2.78초(반경8 #9 같은 wait 2.19초). 결정 경계마다 반경32 스캔 2–3회 비용이다.
- 자연 G2 전체: 관측 프레임 최대 3.15MB(반경8 4.45MB), 로그 874MB(1.16GB), step 벽시계 틱당 68ms(79ms). 공기 창과 새 스캐너 덕분에 긴 실행에서도 반경8보다 작고 빠르다. RPC 상한 16MB와 거리가 멀다.

**모델 입력(실제 tokenizer·CUDA RTX 5070 Ti, 위 시작 관측):**

|과제|Qwen 입력 토큰 새 256칸/이전 64칸|Qwen 1회 지연|NanoJev 후보·최대 경로 토큰|NanoJev forward|최대 GPU 할당|
|---|---|---|---|---|---|
|C4|3,707 / 4,135|1.04초|8 · 3,583|2.05초|9.85GB|
|G2|3,715 / 4,148|0.97초|16 · 3,592|2.94초|9.90GB|
|G3|3,717 / 4,150|1.01초|16 · 3,594|3.32초|10.09GB|
|G4|2,721 / 4,077|0.76초|16 · 2,474|1.76초|9.90GB|

- 4배 많은 칸을 이전보다 적은 토큰으로 전달한다. 8192 상한 안이다. 두 모델(Qwen 4비트+NanoJev) 동시 적재 7.98GB, 최대 10.09GB(16GB 중).
- NanoJev 16후보 forward 약 3초는 본 학습 결정당 시간에 들어간다. #20 예산에서 이 실측을 쓴다. 이전 64칸 입력의 NanoJev 지연은 이번에 재지 않았다.
- 응답은 모두 형식상 유효한 목표 JSON이다. 계획 품질 평가가 아니다.

**발견·수정한 결함:** 반경32 지표면 시작에서 보이지만 16걸음 경로 밖인 원목 때문에 원목 후보가 0개(강제 대기)였다. 접근 불가 자원은 탐색 보행으로 넘기도록 고쳤다(`47a9a9e`, Python만). 측정 도구의 import·토큰 계산 결함도 고쳐 다시 쟀다(원 출력 보존).

**난이도·의미 변화(반경8 결과와 합치지 않음):** 지표면에서 원목·지형을 멀리서 본다. explore(새 열린 칸 16)는 한 번의 이동으로도 거의 항상 완료되어 쉬워졌다. G4 시작 노출은 변하지 않았다. 자연 G4 성공·G2 미달은 반경8과 같은 방향이지만 경로·결정 수가 다르다.

**리뷰(Standards·Spec 독립 2축):** 숨은 정보 조회·토큰 무단 절단 결함 없음. 지적 반영: 호출별 요약 전/후·종류별 누락 기록, 토큰 초과 시 토큰 수 기록(공개 CLI 테스트), NanoJev 규칙 hash, 종류>256 때 드문 종류 보장. 실측으로 해소: 긴 실행 프레임 크기·틱당 비용. 보류: 광선 축 계산 가독성(bridge 변경은 재인증 필요), 매크로 안 보행이 원거리 상태에서 시작하면 map_version이 다름(현재 도달 불가 경로). 수정 뒤 독립 재리뷰는 하지 않았다.

**미실행·남은 일:** 본 학습·C4 평가·Jev/Astra 호출 없음. lock(#20)에 `INPUT_HASH`·fingerprint·반경/창 상수·NanoJev 실측을 고정해야 한다. push·PR·병합·#44 종료는 사용자 결정이다.

## 2026-11-09 — #44 등록·Astra 실제 연결 이연·#10 게시/병합/종료 진행

사용자 명시적 요청으로 [관측 확대 #44](https://github.com/sion0507/Minecraft_RL/issues/44)를 gh CLI로 생성했다. 반경32블록·최소256개 수준의 입력, 자원/위험/설비/기억 보존, 표현/스캐너 개선과 실제 검증은 **#44 구현 시** 수행한다. 기존 저장 관측/실제 tokenizer 분석과 합성 CPU 결과만 이슈에 기록했으며 현재 코드는 변경하지 않았다. 로컬 검토 원시는 artifacts/observation-scope-review-2026-11-09다.

Astra 실제 연결·응답·지원 설정·사용량/과금·지연 검증은 **추후 비교 단계**로 이연한다(사용자 결정). 현재 호출0/실제 미검증이며, 이 미실행은 #10 종료의 장애가 아니다. 단순 접근 확인 유료 진단은 지금 실행하지 않는다. 비교 호출 직전의 키/계정·별도 금액/호출 승인과 실제 metadata/청구 확인은 남아 있다. 사용자의 연결 가능성 기대를 검증 성공으로 쓰지 않는다. #1/#10/#17/#20과 PLAN/PRD에 같은 시점 결정을 반영한다.

현재 e887f4a 위 feat/issue-10-planner에서 기록을 커밋·push·PR 병합·#10 종료한다. 앞 절의 미푸시/Open 기록은 당시 이력이며 이번 사용자 승인으로 게시한다. 최종 실제 상태·SHA·개발 검사·PDF 검수는 artifacts/issue-10/publication.json 및 최신 PDF를 따른다. 게임/모델/API/학습·관측 확대 검사는 이번 게시 때문에 재실행하지 않는다.

게시 직전 fresh 검사: **전체 pytest229개/68.46초**, **mypy src/tests31파일 통과**, `git diff --check` 통과. 원시는 `artifacts/issue-10/pre-merge-{pytest,mypy}.txt`다. 원격 main은 작업시작 기준7a7f8c8이며 기존 구현 e887f4a와 문서만 추가해 PR로 게시한다. .github CI workflow는 없어 로컬 검사를 원격 CI 통과로 표시하지 않는다.

## 2026-11-09 — #10 T09 공통 계획기 구현·실제 Qwen/G1 검증, Astra 승인 대기

**구현:** 선행 #9 Closed/completed와 #10/#1 본문·댓글/PLAN을 확인했다. 기존 Planning/GoalRegistry/run_episode에 공통 입력과 실제 local_7b·Astra HTTPS backend, 공개 smoke-planner를 연결했다. 최초/재생성/규칙 복구 출처·오류 분모·직접 진행을 기존 흐름으로 기록한다. dict/list 목표 필드의 TypeError도 재현 후 수정했다. 고정 선택기의 실제 연결 진단이며 NanoJev/Jev 행동 성능 비교가 아니다.

**설치·고정:** 공개 Qwen2.5-7B-Instruct revision `a09a35458c702b33eeacc393d103063234e8bc28`, Apache-2.0. 인증/결제 없이13파일을 내려받고 SHA-256을 `src/mc_diamond/qwen_files.json`에 고정했다. 정확한 원시 manifest는 `artifacts/issue-10/qwen-files.json`이다. 기존 Torch2.14.0+cu130/Transformers5.17.0에 accelerate1.15.0/bitsandbytes0.50.2/psutil7.2.2를 설치했으며 uv.lock에 고정했다. 샌드박스 DNS·CUDA 접근 실패는 승인 뒤 재실행했고 성공과 합치지 않았다(`qwen-mock.jsonl`, `load-diagnostic.stderr`). sudo·새 약관 동의·로그인·결제는 없었다.

**실제 모델+mock 게임:** 최종 `qwen-final-mock.jsonl` exit0, RTX5070Ti16GB /CUDA13.0. NF4/double quant/BF16·실제4비트·고정/eval 확인, greedy 실효온도0·생성256/총8192토큰 상한이다. 로드9.50초, allocated5,559,966,720bytes(5.18GiB), peak5,870,629,888bytes(5.47GiB), 요청1.315초/815입력·26출력토큰, 유효 collect oak_log1이다. 게임은1결정20mock틱·획득1이며 실제 게임 물리 증거가 아니다. 프롬프트 본문 SHA-256 `49ef69590c951f0f3025ee578fae869a23084a85c8ace46cbba9a6ded69f6ac5`를 기록했다. 최종 오류 경로 보완은 이후 mock 테스트로 검증했고 정상 GPU 경로는 변경하지 않았다.

**실제 Qwen+자연 G1:** `qwen-minecraft.jsonl`/stderr exit0. 기존 G1 snapshot을 사용했고 bridge/runtime/fingerprint 입력은 바꾸지 않았다. 요청4,078입력·26출력토큰/2.541초, 최초 목표유효,5결정216활성틱·원목1 직접획득, reason=goal_completed·clock_mode=paused·pause_verified=true다. 초기오류0/1·재생성0/0·규칙복구0/1, 출처별진행 planner acquired:oak_log=1이다. episode 경과30.873초는 load/reset이전 시간을 포함하지 않으며 전체PC시간으로 해석하지 않는다. 검사 후 `restore.json`/stdout의 G1 reset=observe·0틱·빈인벤토리·체력20 및 Java 서버 종료를 확인했다. 실제 게임은1회만 실행했으며 보고서/오류경로 수정 때문에 재실행하지 않았다. C4/다이아/일반화 결과가 아니다.

**Astra:** 공개 후보 OpenRouter endpoint/model과 공개 표준요율은2026-11-09 공식 페이지를 재확인했다(`astra-access.json`). 실제 제공처/계정 접근·버전·지원옵션·응답·사용량/과금·호출지연·별도 승인금액/호출수는 미확인이다. 질문했으나 아직 확정되지 않아 실제 유료호출0·키읽기0을 유지했다. 상태는 승인/계정설정 대기이며 접근불가/구현오류로 단정하지 않는다. F는 핵심 비교군이다. 승인/키/영속상한 guard, 정상·불량목표/재생성·공통복구·비밀제거·접속/응답오류는mock검사다. 요청당 최악금액은 제공처에서 추론/실패과금까지 검증해야 하며 위반 확인 시 보고비용을 보존하고 해당승인ledger를 영속중지한다. 로컬 사전예약을 실제 청구 확인으로 표시하지 않는다.

**검사·리뷰:** 공개 Planner/기존 목표 검사67개 통과 뒤 독립 Standards2건/Spec3건(서로 중복 포함 결함3건)을 확인했다. 비용 초과 후 재호출, HTTP422 오분류, CUDA 오류 summary 누락을 **3failed→17passed**로 수정했다(`review-red/green.txt`). 문서의 `smoke-planner --config configs/pilot.yaml` 기본 local_7b 경로도 실패 재현 후 보완했다(최종 Planner 검사18개 통과). 최종 전체 pytest **229passed /69.51초**, strict mypy **src/tests31파일 통과**, diff 검사 통과. `mypy .`는 Git 제외 artifacts의 중복 analyze 모듈로 실패했으며 저장소 설정의 개발 범위로 검사했다. 수정 뒤 독립 재리뷰는 하지 않았다. 지적/수정 근거는 `docs/reviews/issue-10-T09-2026-11-09.md`다.

**상태·산출물:** `$implement`의 현재브랜치(main)로컬커밋 범위이며 최종코드기준은 `git log -1`/`artifacts/issue-10/evidence.json`으로식별한다. push·merge·#10종료는미실행/Open유지다. 한국어PDF는 `reports/issue-010-T09-report.pdf`, `reports/issue-010-T09-code-guide.pdf` 각1개, Git제외다. 생성기/중간파일은/tmp에만두고 한글추출·모든글꼴포함·전체페이지렌더가독성을검수한다. 보고서때문에게임은재실행하지않는다.

**후속·미실행:** Jev행동선택#12, 공통6상태계획진단#17, 본학습전예산/lock#20에backend/미확인범위를전달한다. 실제평가군별planner/lock연결은거부하며후속작업이다. 지식부족판정·지식조회·7B학습·PPO/본학습·C4/G4평가·Jev·7B+NanoJev동시VRAM/처리량은미실행이다. 연구/API/PC예산은증액하지않았다.

## 2026-11-09 — #11 T10 게시·병합·종료 진행 (사용자 승인)

병합 직전 fresh 검사: 전체 pytest211통과66.14초(`pre-merge-pytest.txt`), strict mypy src/tests28파일통과(`pre-merge-mypy.txt`), diff 공백 검사통과. `origin/main=e799f6f`는 이 브랜치의 조상이며 기준 문서 커밋 `e839a8e`도 보존해 PR에 포함한다. 보고서/모델/원시는 Git제외다.

사용자가 별도 두 축 리뷰(Standards0/Spec0)를 확인한 뒤 commit/push/PR/원격 main 병합/#11 종료를 요청했다. 아래 "미커밋/Open 유지"는 이 요청 전 검증 시점의 이력이다. 기존 main checkout은 수정하지 않고 전용 브랜치와 GitHub PR로 진행한다. 최종 원격 상태와 커밋은 #11 완료 기록 및 로컬 PDF에 조회 근거와 함께 남긴다. 보고서 상태만 바꾸기 위해 실제 게임/모델 검사를 재실행하지 않는다.

## 2026-11-09 — #11 T10 공개 NanoJev 실제 연결 검증 (전용 worktree, 미커밋)

**범위/상태:** `/home/sion/Documents/projects/RL_projects/Minecraft_learning-issue11`, `feat/issue-11-nanojev`, 시작 HEAD `e839a8e`. #11 Open/댓글0, 선행 #5 Closed(2026-11-05T08:42:43Z)/댓글0, 상위 #1 본문·댓글과 PLAN §§4.2/5.2–5.4/6.1–6.3/12–14, AGENTS·GLOSSARY·CONTEXT·현재 코드/검사를 읽었다. main·다른 세션 파일은 수정하지 않았다. 새 commit/push/merge/PR/이슈 종료·댓글은 하지 않았고 #11은 Open 유지한다.

**구현:** 공통 제한 입력/ID·mask와 목적·예산, 공개 Choice 보존, frozen/no_grad backbone/dropout0, raw 후보 masked mean+목적/시간→독립256/GELU/scalar critic, seeded sampling/argmax·logprob/value·단일 후보 actor 제외, 엄격한 head 저장/복원, `smoke-model` 공개 흐름. 선택 이후 게임 실행/보상은 기존 run_episode/RPC를 사용하며 후보 재생성이나 다른 행동 치환을 하지 않는다. critic 두 개는 새 난수 초기화다. PPO/본 학습 전이는 만들지 않았고 actor_transitions는0이다. 결정·허용된 재사용은 DECISIONS와 third_party의 T10 절.

**설치/실패 이력:** 샌드박스 안 GPU 접근은 실패했지만 승인된 샌드박스 밖 `nvidia-smi`와 PyTorch CUDA 초기화에서 RTX5070Ti16GB·driver595.99.02를 확인했다. 독립 `.tools/uv`/`.venv`/bridge node_modules 설치, 공개 가중치2,385,039,280bytes 다운로드를 수행했다. 최초 pytest185통과/18실패는 Node 의존성 부재였고 npm ci 후 기준203통과(61.84초)다. Node audit의 기존 moderate6건은 기록만 하며 자동 major downgrade를 하지 않았다. 구형 모델 의존성으로 시작한 설치는 bundle의 RoPE 설정을 확인한 뒤 실제 모델 실행 전에 공개 requirements와 같은 PyTorch2.14.0+cu130/Transformers5.17.0/Safetensors0.8.0으로 교체했다. HuggingFaceHub1.33.0 및 전이 의존성은 uv.lock이다. 모델·PyPI 네트워크 실패는 권한을 요청해 재실행했고 sudo·로그인·유료 API는 없었다.

**고정 공개 파일:** NanoJev `unified-games-v1` → revision `047b927b30882a1138fc504821b82ac145a4b81a`; 초기 `best.safetensors` SHA-256 `f68c47d66998231b86b7e91b4ed5e82ae23acf104c8b7cd6d165c3ac7b7ffe1b`. `nanojev.FILES`/`model_loaded`가 사용한9개 파일의 해시를 검사한다. 모델카드의 루트 공개 step-400이며 upstream training_initialization을 쓰지 않는다. 본체596,049,920개, trainable Choice+critics727,940개다. 초기 본체 tensor hash는 `e3d8541282d92608cce23cfd7db551905492d9e54713b76f3df8b479b542a5df`, Choice tensor hash는 `cb104d32dd0db0c0c071f4e88f3af4048aa5d4c57f8c376f31bc24ce8c60aec4`다(파일 SHA-256과 다른 정의).

**실제 모델 + mock 게임 검증:**
- `uv run --locked --extra model --no-sync mc-diamond smoke-model --config configs/model_smoke.yaml`: exit0, model_verified=true, sampling seed11. 저장된 서로 다른 원목 대상 후보2개를 사용했다. public forward/tokenization/EOS pooling/logits FP32/BF16 최대오차 모두0. FP32 logits `[0.3107514381,-0.1800779104]`, BF16 `[0.3125,-0.1796875]`. 확률 `[0.6206215620,0.3793783784]`, ID `obs-0:wood:0`, logprob−0.4770337343이다.
- 명시적 수치 목표의 loss0.4995728731, Choice/local/full 실제 유한 gradient·head hash 변화와 본체 no_grad/hash 불변을 확인했다. 단일 후보 mask에서는 확률1·actor loss제외, full critic만 갱신하고 Choice/local 불변을 확인했다. 끝나면 Choice/local/full 초기 hash 모두 복원했다. 추론 predict는 inference_mode라는 실제 구현을 읽고 학습에 사용하지 않았다.
- `/tmp/issue11-argmax.yaml`(동일 config·모델/fixture 절대경로, mode만 argmax): exit0, 동일 logits/확률·선택 ID·초기 복원, model_verified=true. 약14.84초, GPU peak allocated2,495,388,672bytes(약2.32GiB)다. 단독 짧은 입력의 메모리이며 7B 동시 사용/최대 입력/처리량 결과가 아니다.
- 기본 `configs/pilot.yaml`: **예상 exit1**, 실제 공개 모델의 단일 후보 확률1/logprob0/actor_eligible=false 및 reward.single_candidate 제외를 확인했다. 게임 mock 목표완료true지만 복수 후보 gradient 진단은 없으므로 model_verified=false/diagnostic_completed=false다. 성공 검사로 합치지 않는다.
- 게임은 모두 mock이다(각20활성틱·mock 획득1). 실제 Minecraft 물리·자연 원목/다이아 성공이 아니다. sampling 첫 실행의 tensor→float 진단 경고는 detach로 수정했으며 최종 argmax stderr에는 mock backend 안내만 있다.

**개발/리뷰:** 모델8검사 통과(최신 artifacts/issue-11/model-tests.txt), 전체 pytest211통과66.77초, strict mypy src/tests28파일 통과, diff 공백 검사 통과. tests/test_model.py의 실제 수치 검사는 tiny CPU backbone이며 실제 NanoJev 검증은 위 별도 CLI 원시다. 잘못된 head checkpoint가 actor를 부분 교체하는 문제를 RED→GREEN으로 수정했다. 독립 read-only 코드 리뷰는 공개 source·변경 코드·원시를 확인했고 필수 수정 지적0; 리뷰 자체의 추가 GPU/게임 실행은 없었다.

**산출물/미실행:** 원시 `artifacts/issue-11/{smoke-model,argmax,single-candidate}.jsonl`, stderr와 pytest/mypy/model-tests, load.stdout. 보고서는 `reports/issue-011-T10-report.pdf`, 코드 가이드는 `reports/issue-011-T10-code-guide.pdf`에 로컬 전용으로 두며 Git 제외다. PDF 검수 결과는 아래 완료 기록을 따른다. 게임/bridge/runtime/snapshot을 변경하거나 실행하지 않아 기존 시계 인증을 새로 주장하지 않는다. 실제 Minecraft 연결·7B/Jev/Astra·과금·PPO·본 학습·A/B 실제 evaluate·최종 평가·7B 동시VRAM/처리량·일반화는 미실행이며 T10 진단 통과로 이들을 완료 처리하지 않는다. 연구/API/PC예산 증액도 없다.

**PDF 완료 검수:** 보고서2쪽·코드가이드3쪽의 한글 추출과 대체문자 없음, 모든 폰트 embedded/subset/Unicode mapping을 확인했다. 5페이지 모두1500px로 렌더해 직접 읽었고 잘림·깨진 글꼴·페이지 넘침이 없었다. reports에는 이 티켓의 PDF2개만 있으며 git check-ignore 통과/Git추적0이다. 생성기·추출텍스트·렌더PNG는 /tmp에서만 처리했다. 코드 가이드의 파일/함수/시작줄은 AST로 추출했고 미커밋 코드 SHA-256을 artifacts/issue-11/evidence.json과 교차 확인한다. 보고서용 ReportLab5.0.1은 별도 uv 도구 환경이며 런타임/lock에 넣지 않았다.

## 2026-11-09 — Pathfinder 보류·보존, #36 사람 선택 진단 기록 보충

- **Pathfinder:** 사용자 결정으로 보류했다(DECISIONS 같은 날).
  - Codex 비교 22건과 Claude 추가 실제 진단 13건(복사 서버 25590, 63조건 미인증, `pause_verified=false`)의 결과는 `artifacts/claude-pathfinder-review-2026-11-09/report.md`에 있다.
  - 보존 위치: 로컬 브랜치 두 개, 태그 `pathfinder-deferred-2026-11-09`, `archive/pathfinder-2026-11-09/`.
  - main 코드는 바꾸지 않았다.
- **#36 사람 선택 진단 보충(아래 #36 절, 원시 `artifacts/issue-36/human/g2-2.jsonl`·`g4-2.jsonl`):**
  - 두 실행은 사용자 대신 Hermes가 했다. 아래 절의 "사용자가 별도 Claude 터미널에서"를 이것으로 바로잡는다.
  - 로그에서 다시 확인한 값: G2 `goal_completed`·관리자 판정 자연 철광석 3(돌 곡괭이 직접 채굴·드롭 획득)·10결정·활성 1,038틱. G4 `diamond_success`·자연 다이아 `(-133,8,81)` 철 곡괭이 직접 채굴·획득·9결정·활성 526틱.
  - 복사 서버 `worlds/human-copy`(25566)에는 시계 인증서가 없다. 그래서 두 실행 모두 `clock_mode=unverified`이고 CLI가 exit 1을 반환했다(`cli.py` unverified 분기).
  - 선택에는 운영자 월드 정보(광석·동굴 위치)를 썼다. 따라서 이 결과는 "후보 집합에 성공 경로가 있다"는 증거일 뿐이고, 정책 성능 근거가 아니다.

## 2026-11-09 — T12 공통 평가 슬롯과 서버 오류 재시도 구현 (#13, mock 검증)

**기준:** 브랜치 `issue-13-t12`, 시작 main `1c83428`. 결정은 DECISIONS 같은 날 #13 절.

- **구현:** `evaluation.py`(예정 일정·시도·재시도·비용 중단·불가 군·최고 단계·표별 요약), CLI `evaluate`, `configs/evaluation_mock.yaml`(mock 전체 일정), mock bridge의 `server_error_attempts`.
- **개발 검사(mock·공개 CLI, 실제 게임·모델 아님):** 리뷰 반영 후 pytest 203 passed(66.8초, 기존 188 + 새 15), strict mypy `src tests` 24파일 통과(처음 커밋 때 199).
  - 일정: 핵심 22+G4 6+S 1=29, 축소 14+6+1=21, A·B 난수 공유, ID 고유.
  - 최초 서버 오류 → 재시도 성공이 성공 슬롯 하나(시도 2, 최초 오류·두 시도 시간 보존, 시도마다 reset), 두 번 오류면 오류 슬롯·분모 유지, 사망·계약 오류는 재시도 없음, 비용 중단(미실행 2·재시도 미실행 1, 분모 5), Astra 불가 F 미실행, S 슬롯의 규칙 선택기와 별도 S 진단, 실제 backend의 미연결 선택기 거부, 배포 mock 설정의 29슬롯 전체 실행.
  - 변형 검사: 모든 오류 재시도·비용 중단 제거·불가 슬롯 제외·재시도 2회를 넣으면 각각 실패함을 확인하고 원래대로 돌렸다.
- **리뷰 반영(Standards·Spec):** 블록별 교차 실행, 이전 사용액을 합친 예산, S 비용을 0이 아닌 미측정으로 표시, snapshot이 없으면 시작 거부, 시작 실패 시간 보존, `--groups`·`--task` 검증, S 서버 오류 2회 검사. 공통 `error_summary`·`RpcSession.verification_log`로 중복과 비공개 호출을 없앴다. 다시 검사한 결과는 아래 줄이다.
- **참고:** `uv run mypy .`는 이번 작업과 무관한 `artifacts/pathfinder-natural-2026-11-09/raw/analyze.py`(다른 세션 산출물, Git 제외) 때문에 실패한다. 그래서 설정 범위인 `src tests`로 검사했다.
- **실행하지 않음:** 실제 Minecraft 슬롯 실행(S C4 1회는 T22), A/B/J/F 실제 선택기(T10/T11), 진행 중 비용 상한 중단(T11), lock 고정(T19).

## 2026-11-09 — T08 실제 검증: 정보 감사·T04–T07 회귀 각 1회 (#9, #38에서 이관)

**기준:** 코드 `1f081e3`(작업 트리 깨끗), 사용자 승인, DECISIONS #9 절의 사전 등록 범위 그대로. 14:26–15:11, 출력 `artifacts/issue-9/real-1/`. 4차 63조건 인증서를 썼고 모든 실행이 `pause_verified=true`였다. 재시도는 없었다. 같은 PC에서 다른 세션의 `/tmp` 서버 복사본(포트 25565)이 돌고 있었고 건드리지 않았다.

|검사|결과|
|---|---|
|정보 감사(`verify_t07 information`)|exit 0, `information_verified=true`, 23범위|
|자연 G4(`verify_t07 g4`)|다이아 직접 채굴·획득 성공(관리자 검증 다이아 1·철 3), 63결정·3,902틱, 목표 결정 4(매크로 20회 재채택 3)|
|자연 G2(`verify_t07 g2`)|철 0, `active_tick_limit` 12,000틱·195결정, 최저 y=60, 곡괭이 내구도 3 남음. 결함 없음(기록만)|
|자연 G3(`verify_t06 g3`)|descend 완료, 15결정·2,440틱|
|T05 생산·경계(`verify_t05 production boundaries`)|관리자 장면 생산 54결정·1,806틱으로 철 곡괭이 직접 제작(목표 결정 3, 매크로 20회 재채택 2). 도구 없음·연료 없음·위험·취소 통과|
|T04 매크로(`verify_t04 macros`)|관리자 장면 wood·wood_tool·wood_break·wood_drop·취소 통과. wood_hazard·empty는 설계상 목표 미완료(exit 1, `decision_limit`, 오류 없음), 연속 실패 3회 재계획이 각 3번 기록됨|
|reset|네 도구 모두 기준 snapshot 복원 통과|

- **결정 경로 비교(이전 고정 선택기 기록, 관측 ID 제외):** 자연 G4(#37 3차)·G3·T04 wood·wood_hazard·empty(#37 2차)는 선택·결정 수·틱·종료 사유가 모두 같다. 자연 G2(#37 5차, 같은 bridge)는 195개 선택이 모두 같지만 10번째 같은 `stair_down`이 165→182틱으로 달라 마지막 결정 하나가 줄었다. T05 생산은 12번째 같은 돌 채굴에서 이번에는 매크로 안에서 드롭을 주웠고(`acquired cobblestone 1`), 그 뒤 관측이 달라져 19번째부터 선택이 갈렸다. 두 차이 모두 같은 선택의 게임 결과(시간·드롭 줍기) 차이이며, 후보 상한 16·T08 코드로 선택이 바뀐 결정은 없다.
- 이 검사들은 고정 목표·고정 선택기다. 계획기·S·escape/explore는 실제 게임에서 실행하지 않았다.
- #38에서 옮긴 #9 수락 항목(실제 정보 감사·T04–T07 회귀 각 1회)은 이것으로 충족한다. #9의 남은 항목은 #13 S 슬롯 연결(#13 구현 때)이다.

## 2026-11-09 — T08 목표 처리·재계획·규칙 복구·S 선택기 구현 (#9, 실제 게임 검증 전)

**기준:** 브랜치 `issue-9-t08`, 시작 `32e097e`. 결정은 DECISIONS 같은 날 #9 절이다. push·PR은 하지 않았다.

- **구현:**
  - `goals.py`: GoalRegistry(`validate` 형식·즉시 전제조건·제공 상태 거부, `completed` 7종 완료 규칙, `recovery_goal` escape/explore), `Planning`(최초 요청 → 재생성 1회 → 복구, 분자·분모 집계), `ActiveGoal`(완료·연속 실패 3·3,600틱·매크로 20 재계획 사건, GoalStats 행), 모의 `scripted_planner`.
  - `selectors.py`: 공통 selector 계약 `(observation, goal, saved, failures) → SelectionResult`, 고정 첫 후보. `rule_selector.py`: 규칙 기반 S(`s-rules-v1`, 사전식 키·hash·후보별 키 기록).
  - `episode.py`: 결정 전 목표 채택(`goal_decision` 기록), 목표별 후보, 제시·마스크 후보 검사, 목표 ID·출처를 매크로 증거·보상·`progress_by_source`·`goal_outcomes`에 연결, 계획기 집계를 summary에. 과제 완료(`config.goal`)와 목표 완료를 나눴다. escape/explore 후보는 기존 보행·hold·광석 탐색 생성기를 쓴다.
  - CLI `--select rule`(S). `tools/verify_t06.py`의 방향 고정 selector를 새 계약으로 바꿨다.
- **개발 검사(mock·공개 CLI, 실제 서버 아님):** pytest 188 passed(53.7초, 기존 135 + 새 53), strict mypy 34파일 통과.
  - 공개 흐름: 정상 완료 → 재계획 → 두 번째 목표 완료, 잘못된 JSON → 재생성, 전제조건·형식 오류 2회 → 복구 explore(완료 뒤 다시 복구), 연속 실패 3·매크로 20·3,600틱 각각의 재계획, 고정 목표 재채택, reset 후 같은 결정.
  - GoalRegistry 거부 18경우·채택 6경우, 완료 규칙 사건 fixture 12경우(explore·escape는 실제 매크로 연결 검증 전이라 사건 fixture로만 확인).
  - S: 관련성 순서, 위험 회피, 최근 실패 회피(모두 실패면 무시), 동률 저장 순서, 작업량, descend·escape hold, 21개 → 16개 저장 집합에서 유효 ID·마스크, CLI에서 실패한 원목을 피해 다른 원목 선택, 관리자 로그만 다른 두 실행의 선택 동일, 0/1 후보 공통 계약.
  - 변형 검사: 재생성 제거·S 실패 규칙 제거·제공 보유로 완료·연속 실패 사건 제거·S 위험 규칙 제거를 각각 넣으면 새 검사가 실패함을 확인하고 원래대로 돌렸다.
- **리뷰 반영(Standards·Spec 두 축, 같은 날):**
  - 결함: escape에서 hold와 멀어지는 보행이 같은 관련성 0이어서 작업량이 큰 보행이 항상 이겨 S가 hold를 고르지 못했다(escape 완료 불가). 멀어지는 보행을 관련성 1로 고쳤다. 실패 검사를 먼저 넣어 실패를 확인한 뒤 고쳤다.
  - S를 `rule_selector.py`로 분리해 `RULE_HASH`가 S 규칙만 덮게 했다. 완료 사건 표·실패 판정·사건 집계 중복을 `goals`의 하나로 모았다. 계획기 집계가 summary에 검증 없이 들어가던 것을 검증 경로로 바꿨다. 쓰지 않던 상수를 지웠다.
  - GoalStats에 실패 사유별 수와 채택 전 재생성 수를 넣었다. `direction`은 기록만 한다는 것, S의 전제조건은 생성기·마스크가 맡는다는 것을 DECISIONS에 적었다.
  - 숨은 정보 불변 검사는 mock에서 관리자 로그만 바꾼다. mock 관측 schema가 숨은 필드를 거부하는 기존 검사와 함께, 실제 숨은 블록 대조는 사전 등록한 실제 정보 감사가 맡는다.
  - 다시 검사: pytest 188 passed(53.9초), mypy 35파일 통과.
- **실행하지 않음:** 실제 7B·Astra 계획기(T09), #13 S 슬롯 연결(#13 미구현). 실제 정보 감사·T04–T07 회귀는 위 절에서 실행했다. escape·explore 목표와 S의 실제 게임 동작은 미검증이다.

## 2026-11-09 — #38 병합·종료, 실제 검증은 T08 뒤로 (사용자 지시)

- 사용자가 #38의 실제 정보 감사·T04–T07 자연 회귀를 T08(#9) 구현 뒤로 미루고, push·병합·#38 종료와 다른 이슈 문구 수정을 지시했다(DECISIONS 같은 날).
- 이 기록 시점까지 실제 게임 검사는 실행하지 않았다. 아래 #38 절의 결과는 모두 mock·재생성 측정이다.
- 다음 작업: T08(#9) 구현, 그 뒤 #38 실제 검증의 사전 등록과 실행.

## 2026-11-09 — T07C 후보 상한 16개·종류별 자리 배분 구현 (#38, 실제 게임 검증 전)

**기준:** 브랜치 `issue-38-candidate-cap`, 시작 `9f02b5e`. push·PR은 하지 않았다. 결정과 근거는 DECISIONS 같은 날 #38 절에 있다.

- **구현:**
  - `schema.allocate`: 상한 16, 자리 걷기 6·tunnel 5·계단 4·기타 1, 빈 자리는 잘린 후보를 생성 순서대로. 남긴 후보도 생성 순서 그대로다.
  - `CandidateSet.generated`(상한 전 수)·`truncated`(종류별 잘린 수). schema가 합을 검사한다. 결정마다 `candidates` 사건에 함께 남는다.
  - 모든 생성기(`navigation`·`macros`·`production`·`episode.generate_candidates`)가 `allocate`를 쓴다. 생성기 안의 `[:8]`과 자원 생성의 8개 중단을 없앴다.
  - `episode.policy_candidates`: 에피소드의 생성기 선택을 함수로 뺐다. 재생성 도구가 같은 경로를 쓴다.
  - 정보 감사의 계단·tunnel 후보도 `allocate`를 거친다. `verify_t07.py` 접근 보고에 0–16 분포·잘린 결정 수·종류별 잘린 수를 넣었다.
  - `tools/measure_t07c.py`: 기록된 관측·목표를 `policy_candidates`로 다시 만들어 종류별·상황별 수와 토큰을 센다. 게임·모델 추론·API는 쓰지 않는다.
- **개발 검사(mock·공개 CLI, 실제 서버 아님):** pytest 135 passed(49.5초), strict mypy 31파일, `git diff --check` 통과. Standards·Spec 리뷰 지적(README 상한 문구, 실행 증거 검사, 측정 도구의 평균 중복 집계·이름, #1 스펙 문구, 측정 전용 의존성 기록)을 반영했다.
  - 21개(4계단 4·tunnel 5·걷기 8·1계단 4) 광석 탐색 → 계단 4·tunnel 5·걷기 7(빈 자리 1개가 일곱째 걷기)로 16개, `generated=21`, `truncated={move_observed:1, stair_down:4}`, mask 16개, 선택·실행 증거(`macro_steps`)의 후보 ID가 저장 첫 후보와 같음, 두 번 실행해 같은 저장 집합.
  - 13개 이하 → 모두 남고 `truncated={}`.
  - 원목 24대상 → 채굴 16개, `truncated={mine_visible_cluster:8}`, 대상 중복 없음, 보이지 않는 칸 제외.
  - 기존 검사 갱신: tunnel 장면 검사의 "≤8" 삭제, 내구도 10 G2에서 1계단 작업량이 이제 남음(`{2,1}`), 0후보 저장 집합에 `generated:0`.
- **재생성 측정(`artifacts/issue-38/replay.json`, 코드 기준 작업 트리, 기록 관측 730결정):** 고정 월드의 #36·#37 T04–T07 기록과 사람 선택 실행 17개 로그다. T04 원목 3개는 관리자 fixture다. 기록 당시 코드는 로그마다 다르지만 관측은 bridge 출력이라 현재 생성기로 다시 만들 수 있다.

  |상황(도구 분류)|결정|상한 없는 최대|16 초과|잘린 수(6/5/4/1)|
  |---|---|---|---|---|
  |광석 탐색(걷기·tunnel·계단)|242|21|126|걷기 24·계단 329|
  |노출 자원 채굴(채굴·접근 걷기)|44|40|3|채굴 40·걷기 6|
  |하강 G3(hold·걷기·계단)|30|16|0|0|
  |탈출(걷기)|179|5|0|0|
  |생산·단일(제작·화로·설치·대기, 드롭 대기 포함)|54|2|0|0|
  |걷기만(드롭 회수·대상 접근 포함)|181|12|0|0|

  - 상황 분류는 도구가 목표와 생성 종류로 근사한 것이다(`measure_t07c.context`). 드롭 회수(걷기 1개·대기 1개)는 노출 자원이 아니라 아래 두 줄에 들어간다. 어느 쪽이든 잘리지 않는다.
  - 노출 자원의 16 초과 3결정은 모두 #37 2차 T05 생산 실행의 돌 채굴이다. 매번 채굴 10·접근 걷기 6이 남았다.
  - 로그별: G2(#37 3차) 33결정 모두 16 초과, G2(4·5차) 30결정, G4(3차) 7결정. 사람 선택 G2 1차 10결정.
- **토큰 실측(같은 730결정):**
  - 측정 방식: 후보 하나 = `json.dumps({"action_kind", "params", "description"})`(Python 기본 구분자) UTF-8. 후보 집합 = 같은 사전들의 JSON 배열. 토큰은 NanoJev `unified-games-v1`(`047b927b…`)의 `tokenizer/tokenizer.json`(sha256 `be756060…6a4c55506`, Qwen3-0.6B)과 `tokenizers` 0.21.1로 센다(프로젝트 의존성 아님, `uv run --with`).
  - 8개 = 기록된 실행의 저장 집합(당시 코드, 상한 8, 로그마다 코드가 다름). 16개 = 같은 관측을 현재 코드로 재생성한 집합. 두 열은 코드가 달라 엄밀한 같은 조건 비교가 아니다.

  |기준|8개(기록)|16개(재생성)|
  |---|---|---|
  |후보 수(평균/최대)|5.2/8|7.5/16|
  |후보 하나 토큰(평균/최대)|160.5/376|166.5/376|
  |후보 하나 바이트(평균/최대)|279.1/511|285.8/511|
  |후보 집합 토큰(평균/최대)|832.7/2,741|1,257.2/3,249|
  |후보 집합 바이트(평균/최대)|1,455.6/3,814|2,169.5/5,298|
  |NanoJev 경로당 상한 min(8192, 32768/N)|4,096|2,048|
  |경로당 상태+질문 몫(상한 − 최대 후보 376)|3,720|1,672|
  |Jev 32,000바이트에서 상태 몫(최대 집합 기준)|28,186|26,702|

  - NanoJev 경로당 상한은 "질문 하나의 모든 경로가 `max_microbatch_tokens` 32,768 microbatch 하나에 들어간다"는 가정의 계산이다. 경로 템플릿·질문 토큰은 넣지 않았다. 실제 묶음 규칙과 템플릿은 T10에서 확인한다.
  - 결정당 후보 쪽 입력은 평균 약 425토큰 는다. Jev 1.13 공개 요율 US$0.042/백만(2026-10-10 조회) 가정으로 500요청이면 후보 집합만 평균 US$0.026, 최대 집합이면 US$0.068이다. 가정 계산이며 과금 실측이 아니다. Jev 토큰 수는 Qwen3 토크나이저로 센 대용값이다.
  - 원시 관측은 120KB–4.45MB라 두 모델 한도를 모두 넘는다. 상태 요약은 후보 수와 상관없이 T10/T11 adapter가 정한다.
- **미확인(측정하지 않음):** 현재 Jev 요율, `jev-1.13` context(문서 262,144 vs 제3자 자료 32K), NanoJev 학습 데이터의 후보 수 분포(16개 일반화는 T10 진단), Jev 실제 토크나이저, NanoJev microbatch 실제 묶음 규칙.
- **실행하지 않음(사용자 결정 "구현만 하고 나중에"):** 실제 정보 감사, T04–T07 자연 실행 회귀. 저장 후보 집합에 `generated`·`truncated`가 들어가 정보 감사의 입력 해시는 이전 PROGRESS 값과 달라진다. 감사는 한 실행 안의 ore/lava 쌍을 비교하므로 이력과 다른 것은 실패가 아니다. 63조건은 bridge가 바뀌지 않아 다시 받을 필요가 없다(4차 인증서 유효). 다음 작업에서 범위를 사전 등록하고 실행한다. 고정 선택기 궤적이 그대로인지는 그때 확인한다.
- **다음 작업:** #38 실제 검증(사전 등록 후), 스펙 이슈 #1 본문과 #9 수락 기준의 "최대 8개" 수정(승인 후), 상황별 보장은 기록이 쌓이면 다시 정한다.

## 2026-11-09 — PR #39 병합·#36·#37·#8 종료 (사용자 지시)

- 사용자가 사람 선택 진단 결과를 확인하고 PR #39 병합과 #36·#37·#8 종료를 지시했다(DECISIONS 같은 날).
- 복사본 설치의 `pause_verified=false`는 받아들인 사실로 남긴다. 최종 bridge 기준 미실행 회귀는 DECISIONS에 적었다.
- 다음 작업: #38(T07C 후보 상한 16개·종류별 배분), 그다음 T08(#9).

## 2026-11-09 — #36 사람 선택 진단: G2 철3·G4 다이아 직접 획득

**기준:** #36 통과 조건(DECISIONS 2026-11-08 "자연 G2/G4 수락 기준을 가능성 진단으로 변경"). 사용자가 별도 Claude 터미널에서 `smoke-macros --select human`으로 실행했다. 원시 기록은 `artifacts/issue-36/human/`에 있다. 궤적은 `selector=human` 진단으로만 쓰고 학습·성능·checkpoint 선택에 쓰지 않는다.

|시도|코드|결과|
|---|---|---|
|G2 1차 `g2.jsonl` (00:05–00:37)|`0fecd43`(#37 이전)|19결정·1,737틱 진행 중 중단(요약 없음). 위치 y=56, 돌 곡괭이 내구도 66, 철 획득 0. 후보 상한 분석에 썼다(위 #36 절).|
|G2 2차 `g2-2.jsonl` (~11:47–11:53)|`84b6df3`|**`goal_completed`**. 10결정·1,038/12,000 활성 틱·실제 366초. `admin_verified {iron_ore: 3}`. 세 기록 모두 서버 직전 철광석→직후 공기→손 도구 `stone_pickaxe`→드롭 `iron_ore`→`acquired` 사건으로 연결되고 `natural=true`다. 철 위치는 `-109 57 94`·`-109 57 95`·`-108 57 94`.|
|G4 `g4-2.jsonl` (11:53–11:58)|`84b6df3`|**`goal_completed`, `diamond_success=true`**. 9결정·526/18,000 활성 틱·실제 250초. `admin_verified {diamond: 1}`. `-133 8 81`의 `diamond_ore`를 `iron_pickaxe`로 캐서 드롭을 획득했고 기록이 연결된다(`natural=true`).|

- 10번과 9번의 선택은 모두 사람이 했다(`selector_mode=human`). 후보·실행기·성공 판정은 정책과 같고, 후보는 상한 8개다.
- **설치 차이(주의):**
  - 두 성공 시도는 본 설치와 동시에 돌리려고 복사본 `worlds/human-copy/`(server-port 25566)를 썼다.
  - G2·G4 snapshot tree sha256은 본 설치와 같다(`d3381fbe65c7…`·`9561e53bd4c3…`). server.properties는 포트만 다르다.
  - 포트는 fingerprint 입력이라 복사본에는 63조건 인증서가 없다. 그래서 두 시도 모두 `clock_mode=unverified`·`pause_verified=false`다. 정지 동작과 활성 틱 집계(서버 틱 영수증)는 같은 코드지만, 정지 인증된 설치의 실행은 아니다(DECISIONS 2026-11-07 "포트를 나누면 그 인증은 그 설치에 한정").
  - 이 차이를 #36 통과 판정에 받아들일지, 인증된 본 설치에서 다시 할지는 사용자 결정이다.
- **해석:** 같은 snapshot·시작 상태·활성 틱 상한에서 코드가 만든 후보만 골라 G2 철3과 G4 다이아를 직접 채굴·획득할 수 있었다. 이것은 후보 집합에 성공 경로가 있다는 증거다. 정책이 그 경로를 찾는다는 뜻이 아니다. 사용자는 월드를 알고 골랐다.

## 2026-11-09 — T07B 한 칸 단차 이동 구현 (#37, 실제 검증 전)

**기준:** 브랜치 `issue-36-fixed-world`, 시작 `c1338a7`. push·PR은 하지 않았다. 구현 선택과 사전 등록한 검증 순서는 DECISIONS 2026-11-09에 있다.

- **구현:**
  - `navigation.observed_routes`와 bridge `terrain.canStep`·`validPath`: 관측 칸만 쓰는 한 칸 오르기·내리기
  - `moveObserved`: 점프·한 칸 낙하, 지나는 칸 허용, 12블록 뒤 새 단차 금지
  - 슬라임 단차 거부
  - 실제 관리자 장면 `steps`, `verify_t07.py steps`, 정보 감사 `audit_steps`(scope `move_observed_steps`)
- **개발 검사(모의·scripted, 실제 서버 아님):**
  - pytest 129 passed, strict mypy 30파일 통과, `git diff --check` 통과
  - 공개 CLI `smoke-movement`의 후보 생성: 오르기·내리기·3칸 높이 오르기는 내고, 2칸 단차·미관측/막힌 점프 칸·막힌 앞 머리 칸·위험 바닥·슬라임은 거부한다.
  - `fixtures/movement_physics.cjs`(배포 bridge + 설치 물리):
    - 오르기 21틱/3.13블록, 내리기 25틱/3.37블록, 3칸 높이 오르기 21틱으로 완료했다.
    - 2칸·미관측·막힘·magma·슬라임은 1틱 `invalid_path`로 거부했다.
    - 옆 용암과 사라진 착지 바닥은 `observed_hazard`(불안정 경계)로 멈췄다.
    - 늦은 단차 sweep 96회: 84회는 안정 `distance_limit`(최대 88틱/15.45블록)였다. 12회는 fixture 스캔이 보지 못한 칸 때문에 `invalid_path`였다.
  - 기존 평지 행(돌 79틱/15.3222, 슬라임 119틱/15.8764, 얼음 거부, 실패 1틱 0.1)은 그대로다.
- **리뷰:** Standards·Spec 리뷰 지적을 반영했다.
  - 12블록 규칙이 가장자리 위에서 걸리면 400틱까지 멈추던 결함을 두 경우(내리기, 오르기) 모두 고쳤다.
  - 오르기의 y+3 요구를 뺐다.
  - bridge 거부 사례를 fixture에 추가했다.
  - 실제 막힘 장면에 "돌이 유일한 원인"과 정책 경로 일치 확인을 넣었다.
  - 감사의 숨은 칸을 착지 바닥 아래로 옮겼다.
- **실제 검증 1차(`463c3a3`, `artifacts/issue-37/`, 01:17–01:27):**
  - 과제별 reset C4/G1–G4는 통과했다. manifest 위치·인벤토리가 같고, 두 번 reset해도 상태가 같다.
  - **63조건 시계 인증은 62/63으로 실패했다.** `fall` 0초 3회차가 `scene_prepared=false`였다. 클라이언트 속도가 `[0,0,0]`이었고(다른 낙하 회차는 −0.0784), 위치 drift는 0이었다. 같은 모양은 #32 tick-wait 실행 때 낙하 8회에서 나온 적이 있다. 그 뒤 인증 실행에서는 없었다. `clockTrial`·`advance`는 #37에서 바뀌지 않았다.
  - `verify_t07`은 시계 assert에서 멈췄다. 정보 감사·단차 장면·tunnel·구성 fixture·자연 G2/G4는 실행되지 않았다. 새 인증서가 없어 T06/T05/T04 회귀도 실행되지 않았다. 끝에 한 G4 복원은 통과했다.
  - 기존 인증서 `f724d1c6…`는 그대로다(`clock-before.json`).
  - 사전 등록 규칙에 따라 다시 실행하지 않았다. 재시도 여부는 사용자 결정을 기다린다.
- **실행 스크립트 결함과 #36 기록 정정:**
  - `run-verification.sh`의 `echo "$(date -Is) … exit=$?"`는 `$(date)`가 `$?`를 0으로 바꿔서 항상 0을 적었다. #36 스크립트에서 복사한 결함이다. #37 사본은 고쳤다(`local rc=$?`).
  - 그래서 #36 `status.txt`의 "reset·T07·T06·T05 exit 0"은 틀렸다. 실제 #36 T07은 `AssertionError: natural g4/g2 ended in repeated_stall`로 실패했다. 그 앞의 시계 63/63·정보 감사·tunnel·구성 fixture는 통과했다. T06·T05는 traceback 없이 끝났고 reset도 통과했다. T04는 사용자 요청으로 중단했다. #36 `status.txt`에 정정 메모를 덧붙였다.
  - #36 자연 G4(40결정/918틱)·G2(160결정/2,224틱)의 `repeated_stall` 원인은 같다. 봇이 관측 위험 반경 1.5블록 안에 들어갔다. G4는 보행 중 용암 1.43블록, G2는 계단 굴착 뒤 노출된 물 0.92블록이었다. 이 상태에서는 매 매크로가 시작 시 `terrain.danger`로 1틱 만에 멈춘다. 빠져나갈 후보가 없어 같은 정지가 20회 반복됐다. #36의 진행 차단 조건인 실행기 결함이며, #37 이전 코드에서 나왔다. 처리 방법은 사용자 결정을 기다린다.
- **위험 반경 갇힘 수정(사용자 결정 "양쪽 수정"):**
  - 경로는 반경에 들어가지 않고, 반경 안에서는 멀어지는 보행만 한다. 반경 안에서는 탈출 보행만 후보로 낸다. 실제 `escape` 장면을 추가했다(DECISIONS 2026-11-09).
  - 개발 검사: pytest 131 passed, strict mypy 30파일 통과.
  - 공개 CLI: 반경 1.41블록 칸을 지나는 보행을 내지 않는다. 반경 안(1.0블록)에서는 방문한 칸으로 가는 탈출 보행만 낸다.
  - 물리 fixture: 반경 안에서 멀어지는 보행은 18틱/2.15블록으로 완료했다. 가까워지는 경로와 반경 안 착지는 1틱 `invalid_path`로 거부했다. `step_hazard`는 이전에는 걷다가 4틱에 멈췄고, 이제는 처음부터 거부한다.
- **실제 검증 2차(`d3268bf`, `artifacts/issue-37/run-2/`, 08:31–09:11, 고친 실행 스크립트):**

  |단계|결과|
  |---|---|
  |과제별 reset C4/G1–G4|통과|
  |63조건 시계 인증|**63/63 통과**. 새 fingerprint 인증서(`clock-after.json`). 1차 fall 실패의 재시도다.|
  |정보 감사|통과(733초). 단차 쌍: 오르기 23틱·내리기 18틱, ore/lava 입력 해시 `c830f674…`가 같다.|
  |tunnel 장면 6개|통과|
  |단차 장면|막힘 거부 1틱 `invalid_path` → 오르기 23틱 → 내리기 18틱 → 3칸 높이 오르기 22틱(모두 `path_completed`·안정·정지 인증) → 탈출(마그마 1.0블록에서 18틱 뒤 3.15블록, 안정)|
  |구성 fixture|다이아 1 직접 획득, 지급 다이아는 미집계, 철 1 직접 획득|
  |자연 G4|**실행기 결함 실패**: 20결정·1,281틱 뒤 `protocol_error`. 단차 경로가 시작 칸 바로 위(y+4) 턱으로 이어졌다. 방향이 없는 끝점이 아홉 번째 보행 후보가 되어 `CandidateSet` 8개 상한 검증에 걸렸다. #37 결함이다. 그때까지 최저 y=11, 계단 16, 채굴 41, 철 5·석탄 8 관측, 다이아 노출 0.|
  |자연 G2|실행 안 됨(T07이 G4 assert에서 멈춤). 끝의 G4 복원은 통과|
  |T06(stairs, g3)|통과. 계단 장면 12개 기대 사유, G3 15결정·2,440틱 목표 달성|
  |T05(production, boundaries)|통과. 생산 51결정·1,759틱(#36 실행 49·1,659), 경계 4장면·reset|
  |T04(macros)|통과(`wood_hazard`·`empty`의 exit 1은 기대 결과)|

  - 수정 커밋 작업 중 실행이 작업 트리를 읽을 수 있었다. 그래서 수정본을 09:00:14에 stash로 빼고 2차 종료 뒤 되돌렸다. 편집 시간대(08:59–09:00)에는 T06의 프로세스 내 계단 장면만 돌았고(08:58:29에 `d3268bf` 모듈 적재), 새 `mc-diamond` 하위 프로세스는 시작되지 않았다. 따라서 2차 결과는 모두 `d3268bf` 기준이다.
- **시작 칸 열 끝점 수정:** 시작 칸과 같은 열에서 끝나는 보행은 후보로 내지 않는다(방향마다 하나, 최대 8개). CLI 회귀 테스트를 추가했다. 2차 G4 마지막 관측으로 다시 만들면 후보 8개가 정상 생성된다. pytest 132 passed, strict mypy 통과. 후보 생성은 fingerprint 밖이라 2차 시계 인증서는 유효하다.
- **실제 검증 3차(`dce2c9e`, `artifacts/issue-37/run-3/`, 09:59–10:18):** 사용자 결정 범위(정보 감사·자연 G4·G2). 시계 인증은 2차 인증서로 유효했다.
  - 정보 감사: 통과.
  - **자연 G4: 고정 선택기로 다이아 직접 채굴·획득.**
    - 63결정·3,902틱, `goal_completed`, `diamond_success=true`, `admin_verified {diamond:1, iron_ore:3}`, `pause_verified=true`.
    - 최저 y=6, tunnel 64칸, 계단 16, 채굴 173.
    - 굴착 중 용암 2칸과 다이아 1개(`-142 7 116`)가 노출됐다. 갇힘(`repeated_stall`)은 없었다.
    - 가능성 진단이라 기록만 한다. 학습 정책 성능이나 다른 월드 일반화가 아니다.
  - **자연 G2: `repeated_stall`(실행기 결함).**
    - 33결정·1,056틱, 최저 y=61, 계단 17, 채굴 32, 철 관측 0, 내구도 99.
    - 결정 8의 `stair_down`이 목표 칸 중심 `x=−115.5`를 0.53블록 지나쳤다. 봇 중심이 한 칸 낮은 자연 칸(`x=−117`, 바닥 y=61) 위로 넘어갔고 `observed_hazard`(26틱)로 멈췄다.
    - 몸은 `x=−116` 잔디 바닥에 걸쳐 `on_ground`였다. 그러나 bridge의 서 있음 판정(`terrain.safe`)은 중심 칸만 보므로, 그 뒤 모든 매크로가 시작 시 위험으로 1틱 만에 멈췄다. 20회 반복 뒤 종료됐다.
- **가장자리 걸침 수정(bridge):**
  - `terrain.supported`: `on_ground`이고, 중심 칸의 발·머리가 관측된 빈칸이고, 몸 폭(반폭 0.3) 아래 칸 중 하나가 관측 안전 칸이면 서 있는 것으로 본다. `danger`가 이것을 쓴다.
  - 바닥이 없거나 관측되지 않은 경우는 그대로 위험이다. 정지 경계(`terrain.stable`)는 바꾸지 않았다.
  - 물리 fixture `step_overhang`: 수정 전에는 1틱 `observed_hazard`, 수정 뒤에는 10틱 `path_completed`·안정 경계다.
  - pytest 132 passed, strict mypy 통과.
  - bridge가 바뀌었으므로 새 63조건 인증과 bridge 의존 회귀가 다시 필요하다.
- **실제 검증 4차(`127db20`, `artifacts/issue-37/run-4/`, 10:25–10:51):** 사용자 결정 범위(시계·감사·단차·자연 G2).
  - 63조건 시계 인증: 통과. 새 fingerprint 인증서(`clock-after.json`).
  - 정보 감사: 통과.
  - 단차 장면: 막힘 거부 1틱 → 오르기 23틱 → 내리기 18틱 → 3칸 높이 오르기 22틱 → 탈출 18틱(1.0→3.15블록). 모두 2차와 같다.
  - **자연 G2: `protocol_error: RPC frame too large`(실행기 결함).**
    - 43결정·4,435틱, 최저 y=60, 계단 62, tunnel 1, 채굴 128, 석탄만 관측, 곡괭이 내구도 3.
    - 관측 기억이 9,611칸까지 늘어 관측 JSON이 1.20MB가 됐고, Python RPC 프레임 상한(`MAX_FRAME_BYTES` 1,048,576바이트)을 넘었다. 3차 G4는 최대 1,653칸, 3차 G2는 3,044칸이었다.
    - 단차가 들어간 뒤 지표 흙 지대를 넓게 다니며 계단을 파서 기억이 커졌다. 36,000틱 C4에서도 같은 문제가 생길 수 있다.
  - 끝의 G4 복원 reset은 통과했다.
- **RPC 프레임 상한 16MiB(사용자 결정):**
  - 공개 흐름 테스트를 추가했다. 대체 RPC backend가 20,000칸 관측(1MiB 초과)을 돌려줘도 smoke-episode가 끝난다. 수정 전에는 `RPC frame too large`로 실패했다.
  - pytest 133 passed, strict mypy 통과. bridge가 바뀌지 않아 4차 인증서가 유효하다.
- **실제 검증 5차(`4e7bb16`, `artifacts/issue-37/run-5/`, 11:31–11:49):** 사용자 결정 범위(자연 G2만). 4차 인증서를 그대로 썼다.
  - **자연 G2: `active_tick_limit`(사유 있는 미달, 실행기 결함 없음).**
    - 196결정·12,000틱, `pause_verified=true`, 오류 없음, 철 관측·획득 0.
    - 최저 y=60, 계단 62, tunnel 1, 채굴 128. 첫 계단 17회에 돌 곡괭이 내구도를 쓰고(마지막 3) 그 뒤 지표를 걸었다.
    - 관측 최대 35,792칸·4.45MB로 새 상한 안이었다. 실제 경과 1,045초.
  - 끝의 G4 복원 reset은 통과했다.
- **#37 수락 기준 상태(최종 코드 `84b6df3` 기준):**
  - 개발 검사·실제 단차 장면·단차 정보 감사·DECISIONS/PROGRESS 기록은 했다.
  - 최종 bridge(`a9a046a`)의 63조건·정보 감사·단차 장면은 4차, 자연 G2는 5차, 자연 G4(다이아 직접 채굴·획득)는 3차(이전 bridge `d3268bf`)다.
  - 과제별 reset·tunnel 장면·구성 fixture·T04–T06 회귀는 2차(`d3268bf`)에서 통과했다. 이후 변경 기준으로는 사용자 결정으로 다시 실행하지 않았다.
  - 사람 선택 진단은 아직 안 했다(사용자 실행, #38 순서 결정 필요). push·PR·병합·이슈 종료는 승인 대기다.

## 2026-11-08 — 연구용 고정 월드 교체 준비 (#36, 입력 대기)

**기준:** main `5a1a316`. 게임·검사는 실행하지 않았다. 진행 중인 Minecraft/검사 프로세스가 없는 것을 확인했다.

- 사용자 결정으로 연구 환경을 자원 접근성을 확인한 고정 시드 1개로 바꾼다(DECISIONS 2026-11-08 "고정 월드 교체", PLAN §4.4).
- 이번에는 문서와 이슈만 준비했다. PLAN v1.10·PRD v1.3·GLOSSARY·DECISIONS를 고치고 [#36](https://github.com/sion0507/Minecraft_RL/issues/36)을 만들었다. 코드·설정·월드·snapshot·백업은 아직 하지 않았다.
- 기존 환경(시드 `20261102`, 시작 `[-240.5,65,186.5]`, G4 y=11 방, fingerprint `d482a51c…c598`)은 보존만 한다. 추가 분석·재검증은 하지 않는다.
- 같은 날 사용자 결정으로 자연 G2/G4 수락 기준을 가능성 진단으로 바꿨다(DECISIONS 최상단). 통과 조건은 사용자가 매크로 후보만 골라 성공하는 사람 선택 진단이다. PLAN §5.2.1·PRD·#8·#36 본문을 고쳤고 #8에 #36 연결 댓글을 남겼다.
- **후속 개선 후보(미결정, 본 학습 lock(T19 #20) 전에 정함):** 후보 상한 8개 안의 자리 배분이다. 2026-11-09 사람 선택 G2 1차 기록을 다시 세어 봤다. 지표(y=65)에서는 상한 없이 후보가 15–21개 나오는데 7–13개가 잘렸고, 주로 걷기가 잘렸다. 계단 4개와 tunnel이 앞자리를 먼저 차지하기 때문이다. 지하(y≤61)에서는 9–13개 중 1–5개가 잘렸다. 선택지는 두 가지다. (A) 8개는 유지하고 종류별 자리를 배분한다(예: 걷기 3·tunnel 3·계단 2, 남는 자리는 다른 종류로 채움). (B) 상한을 늘린다(예: 16). B는 PLAN §2의 연구 명세 변경이고, NanoJev 입력 길이·Jev 결정당 비용·PPO 탐색 부담·§5.2의 "의미 있는 차이"를 함께 검토해야 한다. 어느 쪽이든 후보 생성 코드는 fingerprint 밖이라 63조건 재인증은 필요 없다. 하지만 정보 감사와 T04–T07 자연 실행 회귀는 다시 해야 한다.
- **다음:** 사용자가 #36 양식으로 버전·시드·시작·동굴 입구를 주면 백업 → 새 월드 생성 → C4/G1–G3 준비 → G4 제안·확인 → 새 fingerprint 검증 순서로 진행한다.

## 2026-11-08 — T07 #8 결함 수정 후 자연 G2 2차: 철3 미달 (#8 Open, `issue-8-t07`, push 안 함)

**기준:** `d86ce4b`, 작업 트리 깨끗. 사용자 승인으로 1차 결함 두 개를 고쳤다. 내용과 2차 사전 등록은 DECISIONS 2026-11-08 "G2 1차 미달 결함 수정" 절에 있다. 원시 자료는 `artifacts/issue-8/attempt2/`에 있다.

|검사|결과|
|---|---|
|개발(mock/scripted)|pytest 116 passed(반복 정지 종료 테스트 추가), mypy 30파일, `stair_macros.cjs`(모래 자기 칸·다른 블록·바닥 미관측)·`diamond_macros.cjs` 통과. 실제 검증과 별개다.|
|미인증 사전 확인|`preflight-3` tunnel 장면만. `pause_verified=false`라서 증거가 아니다.|
|시계|63/63, `pause_verified=true`. 새 fingerprint `d482a51c65e3498799d756b5971b6b7728660cd526198eb738a946bf606dc598`. `ab713f1a…`을 승계하지 않는다.|
|정보 감사|exit0, `information_verified=true`.|
|tunnel 장면 6개(관리자)|기존 5개는 틱·블록 수가 1차와 같다. 새 `tunnel_sand`: 첫 tunnel이 11틱에 `observed_hazard`(모래가 발 칸 [-241,100,186]을 채움). 둘째 tunnel이 그 모래부터 파고 2칸 `tunnel_completed`(58틱, `stable_boundary`).|
|구성 fixture 3개|1차와 같다. diamond/iron은 연결 1건이고 `natural=false`라서 `diamond_success=false`. 지급 다이아는 0.|
|자연 G4 smoke|1차와 같다. 2결정·49틱, `admin_verified={"diamond":1}`, `diamond_success=true`. 시작 방 벽의 노출 다이아라서 탐색 증거가 아니다(snapshot은 바꾸지 않음).|
|**자연 G2 2차(사전 등록 1회)**|**미달.** exit1, `repeated_stall`, 93결정·1,073활성틱·174.7초, 철 0, `admin_verified={}`. y65→60, tunnel 17칸·계단 4칸·47블록. 관측 광석은 철 1([-241,57,210])·석탄 2.|
|reset|G4 복원 통과.|
|T06 회귀|exit0. 계단 장면 12개의 사유·틱이 T06과 같다. 자연 G3 15결정·2,196틱으로 같다.|
|T05 회귀 1회째|**실패**(exit1). 제작 128결정 `decision_limit`, 원목3·조약돌13·철 0. 경계 3종은 결과 기록 전에 중단됐다. 원인은 아래에 있다.|
|T04 회귀 1회째|**실패**(exit1). wood_hazard가 12결정 안에 원목을 줍지 못했다(이전 10결정). 마지막 reset은 서버 `backend_error`였다. 나머지 장면과 취소는 통과.|
|T05 회귀 2회째|exit0. 제작 50결정·1,683틱, 원목4·조약돌11·철광석3·철괴3. 경계 3종 각 1틱, 취소·reset 통과.|
|T04 회귀 2회째|exit0. 1·81, 3·103, 3·113, 10·70, 2·40, 0후보 12·240(exit1 예상). 취소·reset 통과.|

원시 재계산: 5개 에피소드 모두 스텝 틱 합 = 요약 `active_ticks`, event ID 중복 없음, 전 스텝 `pause_verified=true`.

**G2 2차 경과:**
- 결정 0–3은 1차와 같다. 계단 4 → 남쪽 tunnel 8 → `unsafe_floor` → 동쪽 tunnel 중 모래가 발 칸을 채우고 `no_progress`.
- 결정 4에서 수정이 작동했다. 동쪽 tunnel이 발 칸 모래 [-240,61,205]부터 파고 2칸을 더 나아갔다(111틱).
- 그때 물 [-237,62,206]이 노출되어 `observed_hazard`로 멈췄다. 물이 흘러들어 봇이 물에 있는 스텝이 27회였고 [-238.6,60,208.6]까지 밀렸다.
- 결정 13부터 후보 0개인 강제 대기가 71회였고, 대기도 위험 때문에 1틱씩 멈췄다. 철은 관측 35에 처음 보였지만 이미 물 속이라 다가갈 후보가 없었다.
- 위치·지도·인벤토리가 바뀌지 않는 1틱 스텝 20회로 `repeated_stall` 종료했다. 1차처럼 45분을 소모하지 않았다(174.7초).
- 침수 복구는 기존 결정상 T08 책임이다. 사전 등록대로 재시도하지 않았다. 서버 오류가 아니다.

**T05/T04 1회째 실패 판단:**
- T05 제작: 원목 드롭 위치가 달라 봇이 다른 곳에서 조약돌을 캤다. fixture 바닥은 한 겹짜리 공중 바닥이라 캔 자리가 구멍이 됐다. 구멍에 둘러싸인 위치에서 계단 4방향이 `unsafe_floor`였고, 이후 후보가 0개였다. 손에는 나무 곡괭이를 들었고 돌 곡괭이는 인벤토리에만 있었다.
- 이 경로는 이번 수정(낙하 블록 자기 칸, 1틱 반복 정지)을 쓰지 않는다. 두 기능 모두 발동하지 않았다. 다만 T07의 철 탐색 후보 순서도 같은 막다른 곳에서는 도움이 되지 않는다.
- 드롭 산포에 따라 결정 수가 50·55·61·128로 달라진다. 구성 fixture가 막다른 곳에 빠질 수 있다는 사실은 남는다.
- T04 wood_hazard는 드롭을 줍는 경계 사례다. 마지막 reset의 `backend_error`는 서버 쪽이다. 각 1회 재실행한 결과를 위 표에 함께 적었다. 실패한 1회째를 지우지 않는다.

**#8 상태:** 자연 G2 수락은 1·2차 모두 미달이므로 완료가 아니다. commit은 `issue-8-t07` 로컬에만 있다. push·PR·병합·이슈 종료·G4 snapshot 변경은 하지 않았다.


## 2026-11-08 — T07 #8 인증 실행: 자연 G2 철3 미달 (#8 Open, 브랜치 `issue-8-t07`, push 안 함)

**기준:** `ee76c2c`, 작업 트리 깨끗(`manifest.json` `worktree_dirty=false`). 원시 자료는 `artifacts/issue-8/final/`(12:35–13:44)에 있다. 결정 근거는 DECISIONS 2026-11-08 절이다.

|검사|결과|
|---|---|
|개발(mock/scripted)|pytest 115 passed, mypy 30파일, `stair_macros.cjs`·`diamond_macros.cjs` 통과. 실제 검증과 별개다.|
|시계|63/63, `pause_verified=true`. 새 fingerprint `ab713f1a44cda98ea4f9636f4745f3f969e88004743e9405d3ec9e0962090495`. 이전 `c6760e81…`을 승계하지 않는다.|
|정보 감사|exit0, `information_verified=true`, `hidden_hazard_peek=false`. 새 범위 `diamond_mining`·`tunnel`·`tunnel_exposure`·`tunnel_iron_exposure`가 숨은 광석/용암 실제 쌍에 들어갔다.|
|관리자 tunnel 장면 5개(자연 과제 아님)|8×2 `tunnel_completed` 201틱·16블록·8칸, 2×3 69틱·6블록, 내구도 1 곡괭이 `tool_broken` 9틱, 남은 예산 30틱 `active_tick_limit`(시작 활성 17,970), 무도구 `invalid_tunnel` 1틱. 모두 `stable_boundary`·`pause_verified`.|
|구성 fixture 3개(`natural=false`)|`diamond`: iron_pickaxe 파괴→드롭 267→`acquired` 연결 1건, 그러나 `diamond_success=false`·`admin_verified={}`. `diamond_given`: 지급 다이아는 `acquired`·기록 0, exit1. `iron`: stone_pickaxe→iron_ore 연결 1건.|
|자연 G4 smoke|exit0, 2결정·49틱. 시작 방 벽의 자연 `diamond_ore` [-240,12,188]을 iron_pickaxe로 파괴하고 그 드롭(엔티티 267)을 직접 주웠다. 서버 판정 before/after·도구·드롭·`acquired`가 연결되어 `admin_verified={"diamond":1}`, `diamond_success=true`다. 아래 주의 참고.|
|**자연 G2 수락(사전 등록 1회)**|**미달.** exit1, `wall_time_limit`(2,700.4초), 2,111결정·2,974활성틱, 철 0, `admin_verified={}`. y65→61, tunnel 15칸·계단 4칸·41블록, 관측 광석은 석탄 1개뿐이다.|
|reset|G4 복원 위치·iron_pickaxe 1·남은 18,000틱 확인(`results.json` reset passed).|
|T06 회귀(`artifacts/issue-8/t06/`)|계단 관리자 장면 12개 모두 기대 사유. 틱 145·55·55·73·64·27·9·400·30·1·100·10이 T06과 같다. 자연 G3는 exit0, 15결정·2,196틱으로 T06과 같다.|
|T05 회귀(`artifacts/issue-8/t05/`)|제작 exit0, goal_completed, 61결정·2,149틱(T06 55·1,805). 직접 원목4·조약돌11·철광석3, 제련 철괴3. 무도구·무연료·위험 경계 각 1틱. 취소·reset 통과.|
|T04 회귀(`artifacts/issue-8/t04/`)|1·81, 3·71, 3·113, 10·70, 2·40, 0후보 12·240(exit1 예상). 취소·reset 통과. wood_tool이 T06(2·52)와 다르다.|

T05·T04 차이: 채굴 직후 관측에서 원목 드롭이 더 멀리 떨어져 남아 있었다(T04 wood_tool: T06은 인벤토리 원목1·드롭0, 이번은 원목0·드롭 [-239.0,100,187.3]). 그래서 줍는 이동이 한 번 늘었다. 드롭 착지는 서버 난수 속도라서 이번 코드 변경 탓으로 보지 않는다. 다만 원인을 실험으로 분리하지는 않았다.

원시 재계산: 5개 에피소드 모두 스텝 틱 합 = 요약 `active_ticks`, event ID 중복 없음, 전 스텝 `pause_verified=true`.

**G2 미달 원인(코드 결함, 서버 오류 아님):**
- 4번째 결정의 동쪽 tunnel이 모래 2칸 [-240,62/61,205]을 캐고 봇이 그 칸으로 들어갔다.
- 위 칸 모래가 떨어져 봇 발 칸을 다시 채웠다. 머리 칸은 공기라 피해는 없었다(체력 20).
- 이후 `terrain.danger`가 "안전하게 서 있지 않음"으로 판정해 모든 매크로가 첫 검사에서 1틱 `observed_hazard`로 끝났다.
- 관측과 후보가 바뀌지 않아 같은 후보를 2,107회 반복했다. 회당 약 1.23초라 45분 상한까지 갔다. 결정 4개 867틱 뒤로는 진행이 없다.
- 결함은 두 가지다. ① 진입 후 자기 칸으로 떨어진 모래/자갈을 처리하지 않는다. ② 같은 즉시 중단이 반복되어도 에피소드나 후보가 끝나지 않는다.
- 사전 등록대로 재시도하지 않았다. 재시도는 서버 오류만 허용된다. 결함 수정 뒤 새 시도를 할지는 사용자 결정이다.

**주의 — G4 smoke의 의미:**
- 고정 G4 snapshot의 관리자 시작 방 벽에 자연 다이아 광석 2개([-240,12,188], [-241,12,188])가 0틱 관측부터 보인다. smoke는 그중 하나를 2결정 만에 캤다.
- 그래서 판정 경로(자연 파괴→적절한 도구→자기 드롭→인벤토리)의 실제 확인일 뿐이다. 탐색 능력의 증거가 아니다. G4 smoke에서 tunnel은 0칸이다.
- 노출되지 않은 상태의 탐색은 자연 G2 실행의 tunnel 15칸과 관리자 장면으로만 확인됐다.
- 이 snapshot이면 G4 평가가 시작 위치에 크게 의존한다. T06에서 고정한 snapshot을 바꿀지는 사용자 결정이다.

**#8 상태:** 자연 G2 수락 미달이므로 완료가 아니다. commit은 `issue-8-t07` 로컬에만 있다. push·PR·병합·이슈 종료는 하지 않았다.


## 2026-11-07 — T06 독립 리뷰 반영·새 fingerprint 재인증 (#7 Open, main 미병합)

이 절이 아래 "#32 위 통합" 절의 현재 수치와 인증을 대체한다. 그 절은 `c905a12` 인증 이력으로 보존한다.

**기준:**
- 별도 Claude code-review 세션이 `issue-7-t06`을 main `a38e67e` 대비 리뷰했다. 리뷰 세션은 pytest·mypy만 재실행했고 실제 Minecraft는 기존 자료만 대조했다.
- 지적을 검토해 코드·테스트를 로컬 커밋 `882d5e8`로 고쳤다. 실행 때 작업 트리에서 바뀐 것은 기존 미커밋 문서 4개(CONTEXT·DECISIONS·PROGRESS·README)뿐이다.
- 결정 근거는 DECISIONS 2026-11-07 "T06 독립 리뷰 반영" 절에 있다.

**리뷰 지적별 결과:**

|지적|판정|조치·근거|
|---|---|---|
|자갈 `block_changed` 재판정이 상한에서 1틱 초과|실제 결함|`ticks < limit`일 때만 1틱을 쓴다. `stair_macros.cjs`에 매크로 상한·활성 예산 회귀를 추가했다(수정 전 11틱 재현, 수정 후 10틱). 실제 기록 전수 검사에서 상한 초과는 없었다. 후보를 대응시킬 수 있는 316스텝은 모두 `max_ticks` 이하였고, 나머지 497스텝은 0후보 대기로 최대 20틱이다.|
|`dig()`의 `required < 1` 거부 누락|의도하지 않은 변경|되살리고 `> 400` 거부와 함께 둔다. T05·T05A·T06 기록 어디에도 `dig_failed`가 없어 실제 결과는 바뀌지 않았다. 이번 T05 회귀도 통과했다.|
|hold/`safe_hold` 숨은 정보 비교|기존 범위로 충족|기존 실제 숨은 쌍의 대기 스텝 14개가 `safe_hold`를 내고, 수량·위치까지 비교된다. hold 후보 생성은 관측만 쓰는 순수 함수이고, 관측 동일성은 쌍에서 비교된다.|
|G2 `iron_ore` 중단 경로|실제 미비교였음|실제 실행에서 철이 한 번도 노출되지 않았다. 정보 감사에 G2 정지 목록(`diamond_ore`, `iron_ore`)의 숨은 철/용암 실제 쌍 `stair_iron`을 추가했다.|
|`acquired` 과소 집계와 #8 `direct_acquired`|원인 확인|아래 "#8로 넘기는 사실" 참고. stderr 진단만 추가했다.|
|`lowest()`·`held` docstring·단일 후보 테스트|정리|`first_exposed`(결정 순서의 첫 노출)로 바꿨다. docstring은 "carried (inventory, not hand)"로 고쳤다. 생산 테스트는 미방문 이동 정확히 1개, 마스크 전체, 나머지 계단의 철 정지 목록까지 검사한다.|
|`stop_rule_id`·Python/JS 기하 중복|변경 없음|모듈별 정지 규칙 ID 관례를 따른다. Python은 사전 필터이고, 실제 판정은 bridge가 매 틱 한다. 근거는 DECISIONS에 있다.|

### 최종 실제 검증 (`artifacts/issue-7/review-final/`, 22:33–23:21, 48분)

|검사|결과|
|---|---|
|개발|pytest 101 passed, mypy 24파일, Node 문법 통과. mock/scripted이며 실제 검증과 별개다.|
|즉시 동기화|3장면 exit0.|
|시계|63/63, `pause_verified=true`. 새 fingerprint `c6760e81b4605129b69fc793730b6015b852a422c3ff5048357044f314c81db1`. 이전 `ab5f045f…`를 승계하지 않는다.|
|정보 감사|exit0, 증거 29건(이전 28 + `stair_iron`), 561초, `information_verified=true`. 숨은 철/용암 쌍은 다이아/용암 쌍과 같이 2번째 호출 18틱에 `ore_exposed`/`observed_hazard`로 갈렸다. 그 전 결정은 동일하다.|
|관리자 장면 12개|전부 기대 사유. 틱 145·55·55·73·64·27·9·400·30·1·100·10은 이전과 같다. 자연 과제 결과가 아니다.|
|자연 G3|exit0, 15결정·2,196틱·127.5초, y65→9, goal_completed. 15결정 모두 사유·틱·위치·내구도가 이전과 같다.|
|G2 4방향|남 3,241·서 3,207·북 3,416·동 1,271틱. 64결정 모두 사유·틱·위치·내구도가 이전과 같다. 철0, 남쪽 exit1은 철3 미달로 예상된 결과다.|
|T04 회귀|1·81, 2·52, 3·113, 10·70, 2·40, 0후보 12·240(exit1 예상). 취소·reset 통과.|
|T05 회귀|제작 exit0, 55결정·1,805틱·155.5초. 직접 원목4·조약돌11·철광석3. 무도구/무연료/위험 경계 각 1틱. 취소·reset 통과.|
|동결|소스 55개·mod·`server.properties` 설정(주석 제외)이 시작·종료 시점에 같다(`frozen-ok`). 이전 검사 스크립트의 주석 포함 해시 결함을 고쳤다. 종료 후 서버 0개.|

원시 재계산(`evidence-recomputed.json`, `recompute.py`): 모든 실행 로그에서 다음을 다시 계산해 이상이 없었다(ALL_OK).
- 스텝 틱 합과 최종 `active_ticks` 일치
- 후보 `max_ticks` 이하
- 전 스텝 `pause_verified`, 중단 근거 존재
- 사건 ID 고유
- `hidden_hazard_peek=false`
- 남은 틱이 음수 아님

T05 차이(51·1,691 → 55·1,805)는 `path_completed`가 8회에서 12회로 늘어난 것뿐이다. 드롭을 주우러 걷는 횟수가 드롭 산포에 따라 달라졌다. 직접 획득량과 다른 사유 횟수는 같고, `dig_failed`는 없다.

### #8로 넘기는 사실 (갱신)

- **`acquired` 과소 집계의 원인은 서버 드롭 병합이다.**
  - 이번 G3에서는 돌 107·인벤토리 107에 `acquired` 106이었다.
  - 진단에 정확히 1건이 남았다. 활성 704틱에 추적 조약돌 드롭이 줍지 않은 채 사라졌고(`drop_gone_uncollected`), 712틱에 다른 추적 드롭이 2개로 수집됐다(`drop_count_mismatch` collected=2).
  - 이전 런에서 빠진 4건은 모두 열의 맨 아래 칸이었다. 위 칸 드롭이 같은 칸으로 떨어지는 자리라 같은 기전으로 판단한다. 그 런에는 진단이 없어 개별 확정은 아니다.
  - 남은 엔티티는 기록 수량 1로 집계되고 사라진 쪽은 사건이 없다.
- **#8 판정 영향:**
  - `run_episode`의 완료는 `acquired_target > 0`과 인벤토리 수량으로 정하므로 병합 때문에 미완료가 되지는 않는다.
  - 다만 "직접 획득 3을 사건/인벤토리와 연결"하는 근거에서는 인접 철 3개가 병합되면 사건이 3개보다 적게 남는다.
  - #8은 수집 시 실제 수량(진단과 같은 `getDroppedItem().count`)과 사라진 추적 드롭을 출처 검증과 함께 귀속해야 한다. 추적하지 않은 엔티티와의 병합이 획득을 부풀리지 않게 해야 한다.
- G2 도달 범위와 `itemDrop` 이름 대응 공백(`grass_block`→dirt, `coal_ore`→coal, `diamond_ore`→diamond)은 아래 절 그대로다.

### 남은 작업

- 리뷰 반영 뒤 재리뷰는 받지 않았다. 사용자가 필요 없다고 판단했다.
- main에서의 fingerprint 실행 확인: 하지 않았다.
- 사용자 지시로 이 기록을 커밋하고, 브랜치를 push·PR·main 병합한 뒤 #7을 종료한다. PR 번호·병합 커밋은 #7 종료 댓글에 남긴다.

보고서: `reports/issue-007-T06-report.pdf`, `reports/issue-007-T06-code-guide.pdf`를 이번 결과로 교체했다. 코드 기준은 `882d5e8`이다. 보고서 때문에 게임을 다시 실행하지 않았다.

## 2026-11-07 — T06 #32 위 통합·최종 fingerprint 재인증 (이력, 리뷰 반영 절로 대체)

이 절이 아래 2026-11-06 T06 절의 "#32 후 재인증 필요"와 현재 수치를 대체한다. 그 절은 #32 이전 틱 코드의 실행 이력으로 보존한다.

**기준:** 사용자가 #32의 main 머지를 확인하고 T06을 맞춰 검증·보완하도록 지시했다. main `a38e67e`(origin 동일, #32 Closed)를 `issue-7-t06`에 merge한 `c905a12`에서 작업 트리가 깨끗한 상태로 실행했다. 코드 충돌은 종료 사유 목록 두 줄뿐이었고 양쪽 항목을 모두 살렸다. 문서는 두 절을 모두 보존했다.

**결론: T06 게임 코드 수정은 필요 없었다.** 틱 영수증·입력 fence·`operation` 변경이 stair 경로의 틱 수를 바꾸지 않았다. `stair_down`은 `operation`을 쓰지 않고 `advance(1,true)`만 쓴다. 이 절 이후의 변경은 문서뿐이며 fingerprint 입력은 바뀌지 않는다.

**런타임:** mod를 재빌드한 `9242817e…6f5b`가 main과 같고, `.fabric`·`libraries`·`mods`·snapshot 5개·`server.properties`(주석 제외)도 main과 같다. fingerprint 입력이라 포트를 바꾸면 main과 비교할 수 없어 25565를 유지했다. 동시 서버는 없었다.

### 사전 검사 (미인증, 기준 아님)

`artifacts/issue-7/post32-preflight-1`: 12장면·G3, 전부 `pause_verified=false`. 여기서 틱 수가 그대로임을 먼저 확인했다.

### 최종 실제 검증 (`artifacts/issue-7/post32-final/`, 16:16–17:03, 46분)

|검사|결과|
|---|---|
|즉시 동기화|3장면 exit0. 산소299=299, 화로 lit=true, drop y100.8808 일치.|
|시계|63/63, 위치 drift 0, `pause_verified=true`. fingerprint `ab5f045fe3e0e62c841a37b118272c4c17ed4a4c8ce3c54e7865fbeb3c0b851f`.|
|정보 감사|28장면 exit0, 533초(이전 846초), `information_verified=true`.|
|관리자 장면 12개|전부 pause_verified=true, 기대 사유 일치, 틱 수는 이전과 12개 모두 동일(145·55·55·73·64·27·9·400·30·1·100·10). 자연 과제 결과 아님.|
|자연 G3|exit0, 15결정·2,196틱·127.5초(이전 457초), y65→9, 56계단·채굴165, 내구도250→85, 불안정 정지0, y=9 `safe_hold` 20틱, goal_completed. 15결정 전부 이유·틱·위치·내구도가 이전과 동일. 다이아 성공 아님.|
|G2 남(기본)|exit1(철3 미달, 예상), 64결정·3,241틱·238초, 12결정 y=21 `tool_broken`, 석탄3, 철0.|
|G2 서|64결정·3,207틱·236초, 12결정 y=21 파손, 석탄3, 철0.|
|G2 북|64결정·3,416틱·246초, 12결정 y=21 파손, 금4, 철0.|
|G2 동|64결정·1,271틱·139초, 6결정 y=45 물 노출, 뒤이어 침수, 0후보57회, 산소300→243, 철0.|
|T04 회귀|맨손1·81, 장착2·52, 파손3·113, 위험10·70, 드롭2·40, 0후보12·240(exit1 예상), 취소·reset 통과.|
|T05 회귀|제작51결정·1,691틱, 직접 원목4·조약돌11·철3·철괴3·철 곡괭이1, 무도구/무연료/위험 각1틱, 취소·reset 통과.|
|개발|pytest 101 passed, mypy 24파일, Node 문법. `tests/`·`stair_macros.cjs`는 mock/scripted다. `stair_macros.cjs`는 `advance`를 대체하므로 영수증 경로를 지나지 않는다. 그 경로의 근거는 위 실제 검사와 `tick_contracts.cjs`다.|

원시 재계산(`evidence-recomputed.json`, 자연 G3·G2 4개·T05·T04 6개): 스텝 틱 합과 최종 `active_ticks` 일치, 전 스텝 `pause_verified`·중단 근거 존재, 사건 ID 고유, `hidden_hazard_peek=false`.

처리량: 이번 런 6개 자연 로그 회귀 a=1.179446초/결정, b=0.050068초/틱. #32 목표 0.06을 T06 로그에서도 충족한다. 모델/PPO/reset을 포함한 본 학습 예산의 검증은 아니다.

동결 검사: 소스 54개와 mod는 시작·종료 해시가 같았다. `server.properties`만 불일치로 나왔는데, 서버가 시작마다 첫 줄 시각 주석을 다시 쓰기 때문이다. 주석 제외 내용은 main과 같고 fingerprint는 주석을 제외하며 모든 세션이 `pause_verified=true`였다. 설정 변경이 아니라 검사 스크립트가 파일 전체를 해시한 탓이다. 원시 `final.log`의 해당 줄은 그대로 보존했다.

### 이전 기준과 다른 수치의 원인

- G2 남쪽 1번째 결정 203→192틱: 차이는 이 결정 하나뿐이다. 같은 칸 `[-241,63,189]`이 이전 런 `grass_block`, 이번 `dirt`로, 잔디 번짐(서버 랜덤 틱) 차이로 보인다. 11틱이 이 칸에서 생겼는지는 로그로 확인되지 않았다. 나머지 63결정의 틱은 같다.
- T04 위험 12·72→10·70: 봇은 움직이지 않았고 체력20 그대로다. 드롭이 수집 범위로 들어와 10결정째 획득했다. 드롭 산포이며 위험 회귀가 아니다. 검사기 단언(`observed_hazard`+`mined`) 통과.
- 조약돌 `direct_acquired` 103: 아래 #8 전달 사항.

### #8로 넘기는 사실

- G2 도달 범위는 이전과 같다. 돌 곡괭이 하나로 세 방향 44계단·y=21(131회 채굴), 동쪽 y=45 침수. 철 관측0. 64결정은 진단 상한이며 10분 소진이 아니다(남은 활성 틱 8,584–10,729). 네 직선 통로의 결과일 뿐 월드 전체에 철이 없다는 뜻이 아니다.
- **`acquired` 과소 집계:** G3에서 돌 107개를 캐서 인벤토리 조약돌도 107개인데 `acquired`는 103개였다(같은 코드의 사전 검사는 107, #32 이전 런은 106). 결정 5·6·7·13에서 각 1개 빠졌고 보충되지 않는다. 물건 손실은 없다. 인접 드롭이 병합되면 살아남은 엔티티 하나만 수집 처리되는 것이 유력한 가설이지만, 경계 관측에 드롭이 없어 로그만으로 확정하지 못했다. G3 완료는 이 값을 쓰지 않아 T06 인수에는 영향이 없다. 철3은 `direct_acquired`로 판정하므로 #8은 같은 집계가 실제 획득을 놓치지 않는지 확인해야 한다.
- `itemDrop`은 블록명과 드롭명이 같을 때만 대응시킨다(stone→cobblestone 예외). `grass_block`→dirt, `coal_ore`→coal은 인벤토리에 들어와도 `acquired`가 없다. `diamond_ore`→diamond도 대응이 없고 `mine_visible_cluster` 허용 목록에도 없으므로, 다이아 채굴을 구현하는 티켓에서 함께 추가해야 한다.

### 남은 작업

- T06 코드의 독립 코드 리뷰는 아직 받지 않았다.
- 원격 push·PR·main 병합·#7 종료는 하지 않았다. 병합 후 main에서 쓰려면 인증서가 그 설치에 있어야 한다(입력이 같아 같은 fingerprint가 예상되지만 main에서 실행해 확인하지는 않았다).
- 침수 뒤 탈출 복구는 T08에서 다룬다.

보고서: 이 worktree의 `reports/issue-007-T06-report.pdf`, `reports/issue-007-T06-code-guide.pdf`를 이번 결과로 교체했다. 보고서 때문에 게임을 다시 실행하지 않았다.

## 2026-11-07 — T05A 틱 위상 수정과 전체 재검증

코드 리뷰가 b0.059591389의 목표 충족을 회귀 분해 효과로 지적했고 사용자가 수정·재인증을
지시했다. 아래 절들의 82e5fe5 수치와 “T04 재검증 중단·G2 미실행”을 이 절이 대체한다.

원인: 클라이언트 물리 50ms 타이머와 서버 틱 타이머가 각자 돈다. 위상이 만나면 입력 확인이
서버 틱을 놓쳐 그 step이 100ms가 됐다(960틱 중246개). 초과분 일부가 a로 흡수되어
a1.539/b0.0596으로 보였고, a를 변경 전 값으로 고정하면 b0.0628, 같은 실행 제작 로그는 b0.0778이다.
수정: 입력 확인이 서버의 다음 틱 대기를 끝낸다(`TickWaitAccess`, 최종 코드 f915adc,
도구 수정 a2c0b9f). 활성 틱 상한은 클라이언트 물리 타이머로 유지한다.

|지표|82e5fe5|최종|
|---|---|---|
|고정 장면 a / b|1.539004862 / 0.059591389|1.195105376 / 0.050003609|
|advance 평균·최대·75ms 초과|60.797ms·101.703ms·246개|47.992ms·52.088ms·0개|
|제작 로그 a / b|0.9929 / 0.0778|1.1809 / 0.0500|
|제작 벽시계|56결정 197.0초|49결정 140.7초|
|자연 G2 벽시계|64결정 446.39초|64결정 165.3초|

필수0.10·목표0.06을 고정 장면과 실제 로그 모두에서 충족한다. b0.0500은 정상 20틱/초이며
그 이상의 가속은 아니다. 모델/PPO/reset을 포함한 본 학습 예산 충분성의 검증은 아니다.

최종 실제 검증(artifacts/issue-32/tick-wait/final-2/):

- 즉시 동기화3장면 통과. 시계 63/63·pause_verified=true·최대 위치 drift 0블록.
  fingerprint `ad28e8582b70af35dcd4b3edd51fa5f10785ae3990ad2627fb5f93c25fef8b20`, mod `9242817e0d3375d8e971af43acb55e47fc34fac3a5330777460c3fc694282f6b`.
- T05 정보감사26조건·제작49결정1657틱·도구/연료/위험 경계·취소/재선택·reset 통과.
  직접 원목4·조약돌11·철광석3·제련철괴3. 관리자 fixture이며 자연 G2 성공이 아니다.
- T04 최종 정보감사 통과(82e5fe5의 미완료 항목 해소). 매크로 7항목 통과.
- T04 기준 비교(결정/틱): 맨손 1/81=, 위험 12/72=, 드롭대기 2/40=, 0후보 12/240=,
  취소 2/121=, 장착 3/103→2/52, 파손 3/51→3/113. 위험·0후보 exit1은 예상 결과다.
- 자연 G2 64결정1778틱·철0·decision_limit·정지인증true·reset 통과. 기존 기준선과 같은
  예상 실패로 exit1이며 자연 철3 통합 인수는 #8에 남는다.
- pytest 80 통과, mypy 통과.

기준값과 다른 항목은 드롭 난수로 규명했다. 장착은 첫 드롭을 채굴 중에 주워 2결정에 끝났다.
파손은 드롭이 경로 끝점에서1.0칸 안이면 회수 후보가 나오고, 밖이면 남은 원목 채굴로 간다.
같은 코드 두 번도 좌표가 다르고(100.583 / 100.750) 이전 기준 두 번도 wait/move로 갈렸다.
제작55/1792·56/1817·49/1657도 0번 step의 드롭 좌표부터 갈린다. 서버 난수를 고정하지
않으므로 동일 궤적을 주장하지 않는다.

시행착오: 첫 시도 tick-wait/final/은 시계55/63으로 실패했다. fall 장면이 비보행 advance(1)을
쓰면서 step 대기 동안 물리 타이머가 도는 우연에 의존했기 때문이다. prepared 기준은 그대로 두고
fall만 advance(1,true)로 바꿔 같은 y104·vy-0.0784 상태를 보장했다.
둘째 시도 T04는 wood_break의 reward_total==1 단정에서 멈췄다. 이벤트는 정상이었고 보상이
드롭 위치에 좌우되는 값이라, 그 장면만 실제 획득량과 일치를 검사하도록 고쳤다.
게임 코드 변경이 아니어서 fingerprint가 같고 멈춘 매크로부터 이어서 실행했다.

후속: 공중 드롭이 회수 반경1.0 밖이면 보이는 드롭을 두고 다른 채굴을 고른다. 이번 파손
장면에서 4회 중2회 발생했다. 후보 생성 변경은 #32 범위 밖이라 두었고 T08 검토 대상이다.

## 2026-11-07 — T05A #32 완료·추가 검증 생략 승인

사용자가 “T05에서 모든 테스트 성공했으면 이전 티켓들도 성공했다고 판단하고
테스트하지 말고 완료로 끝내… 최종 마무리하고 커밋하고 푸쉬”라고 명시 승인했다.
이에 T05 전체 통과를 완료 근거로 채택하고 추가 게임/개발 검사를 중단했다.
T04 전체 재검증과 최종 자연G2 회귀를 새로 통과했다고 표시하지 않는다.

최종 실행 코드 `82e5fe5`(전체 hash는 final-headroom/final-manifest.json).
고정 관리자 장면 wait20/100/200 각3회·960틱, 동일 회귀식의 변경 전
a1.193834879/b0.199745351 → 최종a1.539004862/b0.059591389초/틱이다.
필수0.10과 목표0.06을 모두 충족했다. 느린 표본을 포함한9표본을 모두 보존했다.
기존 유효 T05/T04 최종로그10개 회귀a1.225208660/b0.199272347도 재계산했다.
최종 advance960샘플 평균60.797ms·75ms초과246개·최대101.703ms다.
물리/서버 프레임 대기를 포함한 실측이며 전체 a를 pause 감소로 해석하지 않는다.
모델/PPO/reset을 포함한 본 학습 예산 충분성의 검증은 아니다.

최종 실제 검증:

- 즉시 동기화3장면: 첫 틱 산소299=299, 화로lit true=true,
  drop 둘째 틱 높이100.8808=100.8808. pause/조회 전에 캡처했다.
- 새 시계63/63·pause_verified=true·최대 위치drift0블록.
  fingerprint `ee872782a85ec2d7ecc951767706cfd1fb836591c268b9d5c18f1a92cc99c801`.
- T05 정보감사26조건·제작56결정1817틱·도구/연료/위험 경계·취소/재선택·reset
  전체 통과(exit0). 직접 원목4·조약돌11·철광석3·제련철괴3·제작철곡괭이1.
  시작 제공량은 비어 있다. 관리자 fixture 성공이며 자연 G2 성공이 아니다.
- 기존51결정1702틱 대비 이동8/110→13/248결정/틱(+138틱), 시설 조작−23틱으로
  전체+115틱이다. 채굴 수량/틱·제련200틱×3은 같다. 저장 공개 상태에서 기존51개와
  최종56개 결정의 후보를 재생해 내용/순서/마스크 일치를 확인했다. 공개 드롭
  좌표/획득 시점이 달라 후속 이동·시설 위치가 달랐으며 후보 알고리즘은 그대로다.
  동일 궤적/RNG를 입증했다고 주장하지 않는다. production-comparison.json 참조.
- 개발검사는 전체pytest80통과26.97초·mypy22파일·Node문법/Java빌드 통과다.
  독립 Standards/Spec 잔여 지적0. 늦은 물리/입력 순서·틱 불일치·즉시 중단·
  nonce/연결 정리·미확인 연료 차단의 mock 회귀는 실제 게임과 구분한다.

중단/미실행:

- 최종 T04 정보감사는 사용자 지시로 CLI SIGINT(exit−2), 검사기는assert로exit1.
  finally 기준C4 reset은 통과했다. 이는 최종 감사 통과나 새 구현 결함 판정이 아니다.
  T04 후속 매크로와 최종 자연G2는 미실행이며 추가 재실행하지 않는다.
- 기존 자연G2 유효 실패64결정1778틱·철관측/획득0·decision_limit·정지인증true는
  과거 기준선이다. 이번 코드의 새 결과로 쓰지 않는다. 자연 철3 통합 인수는#8이며
  64결정 진단을12000틱 전체 소진/월드 전체 불가능성으로 해석하지 않는다.
- 앞선 T04 감사의 철 획득 실패는 높이3 기둥의 머리 공간 문제로 규명했다.
  iron만 높이1로 보완했고 엄격한 감사 조건/정책/자연 snapshot은 유지했다.
  실제 두 변형 각58틱/획득1/signature일치와 최종T05 감사26조건으로 확인했다.

같은 원본 Git 저장소의 `issue-32-t05a-resume` 브랜치에서만 수정했다.
main4694d54/T06 읽기전용·추가 폴더 이동 없음. 실행 원시/명령/hash는
`artifacts/issue-32/final-headroom/`; 소실된 과거/tmp 원시는 승계하지 않았다.
사용자 승인으로 최종 기록을 커밋·전용 브랜치 푸시한다. PR/merge/#7완료 처리는
하지 않는다. T06에는 최종 bridge+mod 통합·재빌드와 새63조건/감사/관련회귀가
필요하며 이번 인증을 승계할 수 없다. 모델/API·학습·최종평가·유료호출은 없다.
보고서/코드가이드 PDF각1개는 reports/에만 두고 Git에서 제외한다.
PDF 생성 때문에 게임 검사를 재실행하지 않는다.

사후 게시 확인: 기록커밋559f38f25ed57e96d8413603c4cd89c5008d29c4를 origin의
issue-32-t05a-resume에 푸시했고 원격해시 일치를 확인했다.
사용자 승인 범위/중단/미실행을 #32 완료댓글6702791874에 기록하고
2026-11-07T05:25:56Z에 #32를 CLOSED 처리했다. PR/merge/#7변경은 없다.
보고서2페이지/코드가이드3페이지의 PDF각1개를 reports/에 생성했고 Git에서 제외한다.

## 2026-11-07 — 철광석 감사 fixture의 수집 경로 보완

edc92cf의 final/ 시도는 속도0.057844312초/틱·즉시 동기화3장면·63/63/drift0,
T05 정보감사26조건/제작55결정1792틱/모든 경계/reset을 통과했다.
이어 T04 정보감사는 iron의 직접 획득 부재로 exit1이었다. finally reset은 통과했고
macros/G2는 실행되지 않았다. 실패 원시와 기존 인증을 그대로 보존한다.

실패 로그는 철1 직접 채굴·44틱·인증된 안정 경계·공개 드롭을 보여준다.
기존 높이3 기둥의 맨아래만 캐면 위 광석이 머리 공간을 막아 공개 경로 검사가
거부되고, 무작위 드롭이 수집 반경 밖에 남는다. iron 감사만 높이1로 만들어
기존 공개 보행/수집을 사용한다. no-tool 높이3·자연 snapshot·정책·직접획득1·
한 step·전체 공개 signature 비교는 유지한다. fixture의 실제 Terrain.validPath
검사를 RED→GREEN으로 확인했다.

인증 전 실제 iron 두 변형은 각58틱/1.291498796블록·채굴1/획득1·signature 일치,
C4 reset 통과다. 원시 iron-headroom/. 새 fingerprint의 인증 완료로 세지 않는다.
수정 코드를 커밋하고 final-headroom/에서 필요한 전체 최종 검사를 새로 수행한다.


## 2026-11-07 — 지연 물리 입력 순서 보완·최종 코드 고정

4f22bdf의 속도·즉시 동기화는 통과했지만 독립 Spec에서 늦은 클라이언트 물리가
서버 완료 뒤 적용되는 경쟁 조건을 지적했다. 게임 검증을 SIGINT(-2)로 중단했고
finally C4 reset을 통과했다. raw와 run-status는 artifacts/issue-32에 남긴다.

모의 공개 dispatch의 위치/입력 큐 검사 RED를 확인했다. 물리 완료를 앞당기고
같은 클라이언트 연결의 관리자 nonce 확인 뒤 서버 활성 틱을 실행하도록 수정해
GREEN이다. nonce/플레이어/동결/중복·전송 실패 정리를 검사하며 원래 pause는
유지했다. 새 mod는27fe07bcbbbc100dbcbc4114d08426a66a50007ed1e243d5b722c81bebaa71a6.

실제 지연 주입 보행: 두 경로47틱/6.379288976블록·각path_completed/안정경계,
서버/클라 위치 허용오차 검사 및 C4 reset 통과. 인증 전 exit1/unverified로 보존한다.
원시 delayed-movement/. 새 전체pytest79통과24.46초·mypy22·Node문법 통과.
두 축 독립 검토의 잔여 확정 지적0건이다. 이 코드를 커밋으로 고정한 뒤
새 final/ 폴더에서 속도·동기화·63조건·정보/T04/T05/G2를 검증한다.

## 2026-11-07 — T05A 영속 worktree 복구·최종 검증 재시작

사용자가 작업 재개를 요청했다. 기존 /tmp worktree와 원시 로그가 현재 없고
두 구현 커밋3284ba0/787712f는 Git에 남아 있음을 확인했다. 보존 커밋에서
`/home/sion/.codex/worktrees/327b/Minecraft_learning`, branch`issue-32-t05a-resume`을
생성했다. main4694d54와 Claude의issue-7-t06은 읽기 전용이다. 기존 사용자
파일/브랜치/누락 worktree의 등록은 보존했다. 서버·snapshot·Node 환경은 별도
복사하고 포트25566·전용 uv 환경을 설치했다. sudo/API/새 라이선스/학습은 없다.

마지막 미커밋 시설I/O 수정과 영구 회귀를 대화 패치에서 복원했다. 기본조작마다
실제1틱과 관측 후 정지 I/O를 기다리고, 확인 timeout은 후속 조작을 막고 failed
사건을 남긴다. 소실된 이전63조건·시계/감사 원시는 현재 근거로 재사용하지 않는다.

복구 후 실제 변경 전 고정 장면 wait20/100/200 각3회·960틱은
1.193834879초/결정+0.199745351초/틱이다. 실제 구간별 JSONL도 새로 수집했다.
유효 최종T05/T04 로그10개 회귀도1.225208660+0.199272347로 재확인했다.
경로 artifacts/issue-32/recovery/{before-fixed,final-log-fit}. 제외 단차/preflight는
기준선에 섞지 않았다. 관리자 고정 장면이며 자연 과제 성공이 아니다.

복원 후 개별pytest11통과(7.98초)·mypy22파일 통과. mod재빌드 hash는
c0ff66d5a455075e98ae3fea92ea94d520eaa9909c577b36878626486bbee3fe로 보존 코드와
일치한다. 전체 개발 검사와 새 최종 속도/동기화/63조건/정보 감사·T04/T05/G2를
진행한 뒤 결과 비교와 PDF2종을 마무리한다. push/merge/이슈 종료는 미실행이다.

## 2026-11-07 — T05A 즉시 관측 지연 수정·재인증 준비

Spec 검토의 P1을 실제 재현했다. `sync-red/`에서 침수 첫 틱 산소300/서버299,
화로 첫 틱 litfalse/서버true, drop 둘째 틱 y101/서버100.8808로 모두 실패했다.
`sync-before/`도 첫 산소 차이를 확인했다. 각 진단의 assert/exit1 및 finally reset을
보존한다. 추가 게임 틱 없이 vanilla dirty block/metadata/attributes·슬롯을
보내고 drop 위치+상대이동 기준을 동기화한 뒤 `sync-green/`은 모두 일치/exit0,
C4 reset 통과다. accessor/invoker는 기존 watcher와 vanilla dirty 전송만 호출한다.

첫 최종 시계는57/63 통과/drift0에서 의도적 SIGINT(-2) 중단했다. 검사기 exit1과
결과/리셋을 보존하며 인증 완료로 세지 않는다. 이전688f...mod 및 속도 결과를
새c0ff66d...mod의 인증으로 승계하지 않는다. final-speed에서 같은960틱을
재측정 중이며 이어 새 final-v2-t05의63조건·감사·제작·경계, 별도T04/G2를 실행한다.
수시 mypy22파일/새scripted회귀1개·새mod빌드 통과, 최종 전체 suite는 남았다.
독립 Spec은 P1해결/잔여 확정 지적0, Standards도 위반·smell0이다.

## 2026-11-06 — T05A #32 구현·최종 실제 검증 진행 중

현재 사용자의 즉시 구현 지시로 T05A에 착수했다. 기준 main4694d54에서 새
`issue-32-t05a` 브랜치와 `/tmp/Minecraft_learning-t05a-32` worktree를 생성했다.
main과 T06 worktree는 읽기 전용이며 별도 runtime/snapshot·포트25566을 사용한다.
코드는3284ba0에 커밋했으며 push/merge/이슈 종료는 하지 않았다.

`implement` 스킬(/home/sion/.agents/skills/implement/SKILL.md)을 실제 확인·적용했다.
공개 CLI/RPC와 기존 배포 bridge harness를 테스트 경계로 사용했다. 새 회귀는
기존 코드의 per-tick console polling 때문에 RED, receipt 구현 뒤 GREEN이다.
매 틱 관측·피해 즉시 중단·클라이언트 physics 상한/늦은 physics 대기·예상 밖
실제2틱 보존/실패·nonce 불일치 무시·불량응답·끊김·listener 정리를 mock으로 확인했다.
실제 물리/정지 인증과 구분한다. 제작 baseline10pytest, 새 scripted1pytest,
수시 strict mypy21파일·Java 빌드·Node 문법이 통과했다. 전체 suite는 최종에 실행한다.

실제 속도: 최종T05/T04 유효 로그의 같은 회귀식 재계산은1.225208660초/결정+
0.199272347초/틱. 제외 단차/preflight 로그는 쓰지 않았다. 같은 고정 관리자 장면
wait20/100/200 각3회·960틱은 변경 전1.174859334+0.199932601 → 최종
1.195367608+0.050001196이다. 실제20틱/초에 가깝고 필수0.10/목표0.06을 충족한다.
평균 advance 구간은197.55ms→47.98ms다. receipt만 적용한 중간0.100186100은
필수 미달 시도로 남겼다. 모델/PPO 포함 예산 검증이나 자연 과제 성공은 아니다.

첫 계측은 잘못된fixture scope로 invalid_request, 다음은 sandbox의 flock 실패였다.
권한 실행 후 유효 기준선/최종 측정을 완료했다. 승인된 EULA/기존 바이너리만
별도 복사했으며 sudo/새 라이선스/API/학습/유료 호출은 없었다.
사전 장착/채굴은2결정52틱·원목1, 보행은2결정47틱·6.379블록·위치검사 통과다.
둘 다 인증 전 exit1/pause_verified=false로 보존한다.

최종 시계/회귀: `artifacts/issue-32/final-t05/`에서 clock information production
boundaries 진행 중이다. 완결 전 완료로 세지 않는다. 다음은 별도 final-t04와 g2
출력 폴더이며 G2의 기존 실패 exit1/direct_iron_verified=false/assert를 유지한다.
이후 결과 비교·전체 pytest/mypy·독립 Standards/Spec·한국어 PDF2종을 마무리한다.

원시 경로: artifacts/issue-32/baseline/{final-log-fit.json,fixed-3/},after-fixed/,
after-scheduled/,profile-comparison.json,movement-preflight/. 소스/hash·실패 시도도 보존한다.
T06 코드에는 이번 최적화를 넣지 않으며 이후 최종 코드 통합과63조건 재인증을
별도 수행해야 한다. 자연G2철3의 최종 통합 인수는#8이며 기존 실패를 성공으로 쓰지 않는다.

## 2026-11-06 — T06 격리 브랜치 구현·#32 이전 코드 실제 검증 (이력, 2026-11-07 첫 절로 대체)

**위치:** 브랜치 `issue-7-t06`, worktree `/home/sion/Documents/projects/RL_projects/Minecraft_learning-t06`. 실제 실행은 `f169696`+미커밋 변경에서 했고, 문서만 앞선 `4694d54`로 fast-forward한 뒤 소스 hash 동일을 확인했다. 당시 변경 전체가 미커밋이었고 이후 `c4caf44`로 로컬 커밋했다. main 미변경, push/PR/merge 없음. #7·#32 Open. `implement` 스킬은 모델 호출이 거부돼(`disable-model-invocation`) 이슈/AGENTS 기준으로 직접 진행했다.

**이 근거의 한계:** #32가 끝나지 않아 아래 "실제 검증"은 #32 이전 틱 코드 기준이다. #7은 #32 최종 틱 코드에서 다시 인증해야 하며 이 결과를 승계하지 않는다.

### 사전 검사 (미인증, 기준 아님)

`artifacts/issue-7/preflight-1`(10/11), `preflight-2`(11/11), `preflight-3`(12/12), `preflight-g3`, `preflight-g2`. 전부 `pause_verified=false`다. preflight-1에서 자갈이 파낸 칸을 가려 `block_changed`로 끝나는 결함을 실제로 찾아 수정했다.

### 브랜치 코드 실제 검증 (`artifacts/issue-7/final*`, 동결 해시 시작·종료 일치)

|검사|결과|
|---|---|
|시계|63/63, exit0, 새 fingerprint `604752e2…0975`.|
|정보 감사|28장면 exit0, 846초, `information_verified=true`. stair 쌍은 숨은 광석/용암에서 4계단·145틱 동일, 노출 쌍은 2번째 호출 18틱에 `ore_exposed` vs `observed_hazard`로 같은 틱에 갈림.|
|관리자 장면 12개|전부 pause_verified=true. 4계단145틱·광석/용암 노출 각55틱·석탄 통과73·바닥 용암64·빈 바닥27·파손9·400틱 상한·활성 상한30 truncated·무도구1 invalid·자갈100·물 위 대기10틱 중단(safe_hold 없음). 자연 과제 결과 아님.|
|자연 G3|exit0, 15결정·2,196틱·457초, y65→9, 56계단·채굴165, 내구도250→85, 중단 없음, y=9 `safe_hold` 20틱, goal_completed. 다이아 성공 아님.|
|G2 남(기본)|exit1, 64결정·3,252틱·726초, 12결정(2,225틱) y=21 `tool_broken`, 석탄3, 철 관측0.|
|G2 서|64결정·3,207틱·717초, 12결정 y=21 파손, 석탄3, 철0.|
|G2 북|64결정·3,416틱·759초, 12결정 y=21 파손, 금4, 철0.|
|G2 동|64결정·1,271틱·330초, 6결정 y=45 모래·자갈 위 호수 노출로 안정 경계 중단, 7결정 뒤 침수, 57회 0후보+1틱 중단. 철0, 산소300→244(마지막 저장 관측).|
|T04 회귀|맨손2결정162·장착3·103·파손3·113·위험12·72·드롭2·40·0후보12·240·취소121틱. 위험/0후보 exit1은 예상.|
|T05 회귀|제작54결정·1,826틱, 직접 원목4·조약돌11·철3·철괴3·철 곡괭이1. 무도구/무연료/위험 각1틱, 취소 통과, reset 통과.|
|개발|pytest 99 passed, strict mypy 21파일, Node 문법 통과. `tests/`·`fixtures/stair_macros.cjs`는 mock/scripted이며 실제 검증이 아니다.|

T04/T05 틱이 기준값과 다른 것은 드롭 산포다. 첫 스텝이 같고, 이번 런 공개 관측 88개를 `f169696`과 현재 생성기에 재생한 결과 후보 ID·내용이 88/88 일치했다. T04 파손의 3번째 후보 차이는 두 관측이 드롭 좌표만 달랐고, 드롭만 맞바꾸면 후보도 양방향으로 뒤바뀌었다. 틱 합계·중단 근거·사건 ID 고유성은 `artifacts/issue-7/final/evidence-recomputed.json`에 원시 재계산했다. 시작 시점 manifest의 소스 21개는 현재 트리와 모두 일치한다. 스크립트의 exit1은 마지막 줄 `grep -c`가 잔여 서버 0개를 센 결과이며 모든 단계는 exit0이었다.

### #8로 넘기는 G2 사실

제공 돌 곡괭이 하나와 계단만으로는 세 방향 모두 44계단·y=21에서 내구도가 끝나고(131회 채굴), 동쪽은 y=45에서 침수됐다. 어느 방향도 철을 보지 못했다. 나무가 없어 곡괭이를 다시 만들 경로도 없었다. 64결정은 진단 상한이며 10분 소진이 아니다(남은 활성 틱 8,604–10,730). 네 방향 직선 통로의 결과일 뿐, 월드 전체에 철이 닿을 수 없다는 뜻이 아니다. 철3 자연 획득은 여전히 미달이며 #8 책임이다.

보고서: 이 worktree의 `reports/issue-007-T06-report.pdf` 3쪽, `reports/issue-007-T06-code-guide.pdf` 2쪽. 전 페이지 렌더링·한글 추출·글꼴 포함을 확인했다. 보고서 때문에 게임을 다시 실행하지 않았다.

### 남은 작업

#32 위 재인증은 2026-11-07 첫 절에서 완료했다. 남은 작업은 그 절을 따른다.

## 2026-11-06 — 개정 T05 완료·T05A 착수 가능 (구현 미착수)

**완료:** 사용자 승인으로 개정한 T05 인수7항목을 충족했다. 인수 책임 문서 커밋 `f16969647cd5c2f9cb993afe20d03272de190adb`를main/origin에 푸시하고 실제원격해시 일치를 확인했다. [#6 완료 댓글](https://github.com/sion0507/Minecraft_RL/issues/6#issuecomment-6683924522)을 남기고 #6을2026-11-06T11:38:26Z에Closed 처리했다. PR/merge는 수행하지 않았다. 이 완료 상태 기록도 별도 문서 커밋으로 보존하며 실행 코드는ff75f36과 동일하다.

**자연 G2는 여전히 미달이다.** 유효 기준선64결정/1778틱/철 관측·획득0·정지 인증true를 보존했고, 제외 단차의64/150틱/철0·미인증 결과와 구분했다. 성공으로 체크하지 않았으며 같은snapshot/시작점/돌곡괭이/10분에서 철 발견→적절한 도구 파괴→해당 드롭 직접 획득3의 최종 통합 책임은#8이다. #7은 기존G3와별도G2접근 확인을 맡는다.

[#32](https://github.com/sion0507/Minecraft_RL/issues/32)는Open/ready-for-agent이며 실제blocked_by 조회에서 유일한 선행#6이Closed임을 확인했다. **다음 이슈 T05A에 착수해도 되는 상태다. 이번에는 구현·advance 계측·속도 개선을 시작하지 않았다.** #7/#8은Open/미구현이고 기존선행그래프를 유지한다. 기존실패회귀·최종코드63조건재인증·정보감사·관련T04/T05회귀 조건은모든본문/PLAN에 반영했다.

보고서 `reports/issue-006-T05-report.pdf`2쪽과 코드가이드 `reports/issue-006-T05-code-guide.pdf`3쪽을 최신교체했다. 실제/mock/미인증/미실행·G2미달이관·제외코드·구현ff75f36/인수문서f169696·commit/push/merge/종료/ready 상태를 구분했다. 한글추출·대체문자 없음·모든사용글꼴embedded/subset/Unicode·최종5페이지렌더 가독성을 확인했다. 코드가이드는 파일/함수/시작줄·확인할로직·SHA256을 제공한다. PDF/원시/백업은Git제외,생성중간물은/tmp이며 게임재실행은없다.

남은 위험: 자연G2철3 성공 가능성과 굴착 필요성은 미입증이다. 단차 실험은슬라임거리상한/인증미완료로제외했으며향후채택시별도교정/검증이필요하다. T05A는속도만개선하므로탐색문제해결을보장하지않는다. 모델/API/학습/평가·연구조건/예산변경은미실행이다. 아래 Open/종료전/미완료 문구는각게시·검증시점의 이력이다.

## 2026-11-06 — 사용자 승인에 따른 인수 재배치·최종화

**현행 판단:** 자연 고정 G2 철3은 미달이며 성공으로 바꾸지 않는다. 사용자가 T05를 제작·제련·노출 철 직접 채굴/획득 연결과 검증으로 정리하고 G2를 후속 통합 인수로 이관하도록 승인했다. PLAN §5.2.1/PRD/#1/#6/#7/#8/#32를 이 기준으로 맞춘다. 아래의 #6 Open 유지·종료 금지 문구는 변경 전 이력이며 이 승인으로 대체된다. T05는 개정 기준 충족·커밋/푸시·GitHub 확인 뒤에만 완료하며 T05A 구현은 이번에 시작하지 않는다.

### 코드 범위와 미검증 단차 변경 제외

시작 상태 main `ff75f365026c9ec8600d9d3a4a6a1a67ae2dd1b3`/origin 동일, 단차 관련8파일 미커밋이었다(소스/검사7+계획1). 모든 변경을 패치·파일 사본·SHA-256 manifest로 `artifacts/issue-6/excluded-natural-steps-2026-11-06/`에 보존하고 7개 소스/검사/드라이버를 ff75f36과 바이트 동일하게 복원했다. 계획은 제외 경위의 이력으로 남긴다. 보존 패치 SHA-256은 `538437e2682009e6507b9acdf7693561ca52384ec1208b767376f9597794dc0b`다. 백업 Python 사본 때문에 첫 mypy가 중복 모듈로 실패했고 파일명을 .saved로 바꾼 뒤 strict mypy23파일을 통과했다. 백업이나 사용자 코드를 삭제하지 않았다.

제외한 코드의 실제 단차 fixture는 상행24/하행17틱·위치/착지 확인이었으나 정지 미인증이다. 새63조건·단차 정보 감사는 수행하지 않았고 scripted 슬라임 하강 거리 상한 초과도 미해결이었다. 해당 자연 G2 사전 실행(`g2-natural-step-preflight/`)은64결정/150틱/119.12초·철 관측/획득0, observed_hazard63회·decision_limit·pause_verified=false·reset 통과다. dryland 인근 위험 판정의 원인은 미확정이다. 이 결과를 인증된 기준선/단차 구현 완료/자연 성공으로 합치지 않는다.

### 개정 T05 근거와 후속 책임

복원 후 전체 pytest **78 passed(18.39초)**, strict mypy **23파일**, bridge/minecraft.js·terrain.js Node 문법 통과. 원시 재계산은 기존 실제63조건/26장면/직접 사건·틱 합계/후보 상한·사건 중복 없음/reset을 확인했다. g2-route-fix manifest의 모든 소스 hash가 일치한다. final-3의 navigation/driver, control-final의 navigation 차이는 이전의 공개 후보 누락 수정과 취소 후 재선택 드라이버 보완이며, 기존 실제32관측의 후보 순수 재생32/32 일치 근거를 유지한다. 이번 문서·인수 변경 때문에 게임을 재실행하지 않는다.

|근거|결과·한계|
|---|---|
|실제 시계/정보 감사|final-3:63/63·drift0,26장면 통과. 복원한 bridge/runtime/설정/snapshot fingerprint가 저장 인증6de2893387dc7971a1213cf939e056c07520edef6f6edfede0982b423e832804와 읽기 전용 재계산으로 일치했다. 새 게임 실행이 아니다.|
|실제 제작/직접 철 연결|final-3:빈 인벤토리/관리자 배치 자원,51결정/1702틱. 직접 원목4·조약돌11·철광석3, 직접 제련 철괴3, 직접 제작 철 곡괭이1. 자연 C4/G2 성공 아님.|
|실제 전제조건/제어|control-final:도구·연료 부족각1틱,위험1틱. 취소40틱 actor제외/trace0 뒤 새 제작3틱,총43틱·선택2/실행1. 기준 C4 reset·서버 종료.|
|자연 G2 실패 기준선|g2-route-fix:제공 돌 곡괭이1,64결정/1778틱/446.39초·철 관측/획득0·방문155칸·decision_limit·서버오류 없음·정지 인증true.10분 전체 소진이나 전체 월드 불가능성의 근거 아님.|

T05A는 #6 개정 범위 완료 뒤에만 착수하며 기존 G2 실패를 회귀 기준선으로 보존한다. T06은 기존 G3와 별도 고정 G2 접근/노출/실패 확인, T07은 같은 snapshot/hash·시작점·돌 곡괭이1·10분/12000틱에서 자연 철 발견→적절한 도구 직접 파괴→해당 드롭 직접 획득3의 최종 책임이다. T07 미달 시 #8은 미완료다. #5→#6→#32→#7→#8의 기존 그래프와 #7의 #5 선행을 유지한다. 최종 bridge/fingerprint 변경 때 각 티켓63조건 재인증·정보 감사·관련 매크로 회귀를 요구한다. G2 기존 실패/제외 코드 사전 실패/새 회귀 결함을 구분하고 검사기 assert를 우회하지 않는다.

GitHub 반영 확인: #1/#6/#7/#8/#32 본문과 변경 댓글을 게시 후 다시 조회해 준비한 원문과 모두 일치함을 확인했다. #6 개정 인수7항목 체크, 자연 G2는 별도 미달·#8 이관 문구로 보존, #7/#8/#32 구현 항목은 미체크다. 실제 선행은 #6←#5(Closed), #32←#6(Open), #7←#5(Closed)/#32(Open), #8←#7(Open)로 기존 그래프와 일치했고 역의존은 없다. 재계산·게시 교차확인 결과는 로컬 acceptance-reallocation-check.json에 보존했다. 독립 Spec 지적0, Standards hard breach0·명확성1건(PRD/#1 과거 미검증 문단)을 해소했다.

변경 댓글: [#1](https://github.com/sion0507/Minecraft_RL/issues/1#issuecomment-6683790490), [#6](https://github.com/sion0507/Minecraft_RL/issues/6#issuecomment-6683803025), [#7](https://github.com/sion0507/Minecraft_RL/issues/7#issuecomment-6683827942), [#8](https://github.com/sion0507/Minecraft_RL/issues/8#issuecomment-6683839319), [#32](https://github.com/sion0507/Minecraft_RL/issues/32#issuecomment-6683846771). 댓글 게시의 첫 sandbox 네트워크 실패는 권한 실행으로 재시도했고 게시 후 원문을 확인했다. 당시 #6은 완료 처리 전 Open이었고, 커밋/푸시·원격 확인 뒤 최상단 완료 기록과 같이 닫았다.

게시·최종 문서·PDF 검수와 Git 상태는 아래 완료 확인에 기록한다. 모델/API/PPO/학습/평가·PC180시간 증액·T05A 구현은 하지 않는다. reports 두 PDF는 최신 교체하되 로컬 전용/Git 제외이며 보고서 때문에 게임을 실행하지 않는다.

## 2026-11-06 — T05 재개 후 탐색 후보 누락 수정·최종 인수 미달 보존

사용자가 사용량 제한으로 중단된 T05만 이어서 검증·PDF·커밋/푸시·이슈 절차를 처리하도록 요청했다. 이전의 push 금지는 이 추가 요청으로 대체한다. T05A(#32)나 다른 티켓 구현은 시작하지 않았다. 현재 #6의 고정 자연 G2 직접 철광석3 기준은 그대로이므로 미달인 채로 이슈를 닫지 않는다.

final-3 G2의 마지막 공개 관측을 다시 읽어 도달 경로155개 중 미방문55개가 남았는데도 후보0이던 결함을 재현했다. 방향별 대표 경로를 고른 뒤 방문한 끝점을 버리는 순서 때문에 다른 새 경로까지 가려졌다. 공통 `generate_movement_candidates`가 방향별 미방문 끝점을 우선 보존하도록 수정했다. 후보 최대8·관측 지도·같은 높이·16블록/400틱·실행 방식과 G2 상한은 유지한다. 공개 CLI 회귀 RED→GREEN, 저장된 마지막 G2 상태에서 후보4개 생성 확인. 전체 **78 pytest passed(18.72초)**, strict mypy **23파일**, Node 문법·diff 검사 통과다.

같은 고정 G2를 `artifacts/issue-6/g2-route-fix/`에서 실제 재검증했다. **CLI exit1,64결정·1,778틱(88.9 활성초)·446.39 실제초·철0·decision_limit·서버 오류 없음·paused/인증true**다. 돌 곡괭이1 제공, 방문155칸·철 관측0·경로 완료39·0후보 대기25회다. 저장된 공개 지도 전체의 같은 높이 연결 성분155칸에서 미방문0임도 확인했다. 후보 누락은 보완됐지만 **직접 철3 인수 조건은 여전히 미달**이다. 이는 전체 월드나12,000틱 전체 불가능성의 증거가 아니다. 최종 C4 reset/observe·0틱·빈 인벤토리·체력20 및 검사/서버 종료를 확인했다.

게임/시계/bridge/runtime 변경은 없고 새 G2의 인증도 true라 시계63은 반복하지 않았다. 기존 실제26장면 감사의 공개 관측32개를 수정된 후보 생성기로 순수 재생해 저장된 후보 ID/내용/순서/mask가 **32/32 모두 동일**함을 확인했다(`candidate-replay.json`). 이는 새 실제 감사가 아니라 기존 실제 근거에 대한 후보 재생 확인이다. final-3의 실제 시계63·정보26·전체 제작51결정/1702틱과 control-final의43틱 제어 근거를 함께 보존한다. 최신 통합 재계산은 `g2-route-fix/evidence-recomputed.json`, G2 상세는 같은 폴더 `g2-recomputed.json`이다.

보고서와 코드 가이드는 최종78검사·수정 전후 G2·실제/mock/미실행·커밋/푸시/이슈 상태와 코드 줄/hash로 갱신한다. PDF 생성 때문에 게임을 재실행하지 않는다. 구현과 유효 근거를 현재 브랜치에 커밋·푸시하고 #6에는 충족한 항목과 G2 미달을 기록한다. **#6 Open 유지, 다른 티켓 미착수**가 이번 종료 상태다. 이하 추가 요청 전의 push 금지·77검사·G2 1687틱 기록은 해당 시점 이력으로 보존하며 위 최신 상태가 우선한다.

## 2026-11-06 — T05 구현 보존, 고정 자연 G2 인수 조건 미달

**#6 전체는 미완료이며 Open을 유지한다.** 빈 인벤토리/배치 자원에서의 제작 사슬과 실행 경계는 실제 검증했지만, 관리자 지원 없는 고정 자연 G2에서는 철광석3을 획득하지 못했다. 후속 티켓 자동 착수, snapshot/시드/시작점 변경, 하강/터널 추가, 모델/API/학습, 연구 예산 증액은 하지 않는다. 현재 main의 구현과 검증 기록을 로컬 커밋으로 보존하며 push·PR·merge·이슈 종료/댓글은 수행하지 않는다. 최신 커밋은 `git log -1`로 확인한다.

|구분|실제 최종 결과|
|---|---|
|시계|final-3 exit0,63/63. 고유63·준비63·전후 전체 상태 동일·최대 위치 drift0. 인증 `6de2893387dc7971a1213cf939e056c07520edef6f6edfede0982b423e832804`.|
|정보 감사|final-3 exit0,26장면·710.42초. 기존 관측/보행/목재/장착/대기/드롭/0후보에 제작3틱·설치7틱·화로207틱·철44틱의 숨은 광석/용암 쌍 불변과 벽 개방 양성 대조 통과.|
|배치 자원 제작|final-3 exit0,51결정·1,702틱(85.1 활성초)·413.17 실제초. 시작 인벤토리 비움. 원목4/조약돌11/철광석3 직접 획득, 철괴3 직접 제련·회수, 작업대/나무·돌 곡괭이/화로/철 곡괭이 직접 제작. 지급 철 곡괭이가 아니다. actor0·진단 수집 보상18.|
|전제조건·위험|control-final exit0. 돌 곡괭이 없는 철 채굴·연료 없는 투입 각각 invalid/1실제틱. 관측 용암 위험은1틱·observed_hazard·불안정 경계로 투입 중단. 유효 채굴/투입/제련 사건 없음.|
|취소·재선택|control-final의 제작 준비 지원 장면. 실제 진전20+취소 대기20=40틱을 원 선택에 보존, actor제외/trace0. 새 선택으로3틱에 철 곡괭이 직접 제작. 총43틱·선택 요청2·실행 결정1·목표완료·paused/인증true. 전체 realtime 인증은 아니다.|
|고정 자연 G2|final-3 CLI exit1,64결정·1,687틱(84.35 활성초)·428.40 실제초. 시작 제공은 돌 곡괭이1개, 철 획득0·goal_completed=false·decision_limit·서버 오류 없음·paused/인증true. 직접 철3 인수 조건 미달.|
|최종 복원·종료|final-3/control-final 모두 기준 C4 reset/observe 일치·0틱·빈 인벤토리·체력20 복원. 권한 ps로 검사/bridge/Java 서버 잔여 프로세스 없음을 확인.|

G2 원시 재계산: 시작 `[-240.5,65,186.5]`, 공개 관측 방문100칸, 관측 철 셀0. 경로 완료22·거리 상한3·0후보 대기39회다. 현재 같은 높이의 관측 경로 탐색이 철 확보로 이어지지 않았다. 전체 월드에 철이 없거나 활성 상한12,000틱 전체에서도 불가능하다는 증거가 아니다. 결과를 보고 시작점·월드·규칙·예정 횟수를 튜닝하지 않았다. **재개 시 남은 항목은 고정 자연 G2 직접 철3 조건**이며 기존 통과 검사를 다시 실행하는 일이 아니다.

최종 개발 검사는 전체 pytest **77 passed(19.57초)**, strict mypy **23파일 통과**, Node 문법·diff 공백 검사 통과다. 별도 Standards/Spec 검토 후 확인된 지적을 회귀로 보완했고, 실제 화로 창 재고 문제와 검증 도구의 취소 후 재선택 누락도 보완했다. 상세는 docs/reviews/issue-6.md다. final-3의 초기 취소 검사는40틱 보존만 확인했으며 최신 control-final의43틱 결과로 재선택 근거를 보완한다. 따라서 final-3 manifest와 현재 driver만 다르고 게임/후보/시계 소스는 동일하며 control-final manifest는 전부 일치한다. 시계63·정보26·전체 제작은 반복하지 않았다.

원시: `artifacts/issue-6/final-3/`, `artifacts/issue-6/control-final/`. 재계산 `control-final/evidence-recomputed.json`, `final-3/g2-recomputed.json`. 사전 실패/중단은 아래 기록과 원시에 보존하고 최종 성공과 합치지 않는다. 실제 사망·8개 배치 중단·제공 화로 출력 제외·소비 중 동시 드롭 등 일부 경계는 mock/scripted 검사다. 자연 C4/다이아 성공·모델/유료 API·과금·PPO/본 학습·최종 평가·일반화·전체 realtime은 미실행이며 PC180시간의 충분성을 재확정하거나 증액하지 않았다.

보고서 `reports/issue-006-T05-report.pdf`와 코드 가이드 `reports/issue-006-T05-code-guide.pdf`는 위 미완료 판정·실제/mock/미실행·함수 시작 줄/코드 hash·Git 상태를 담는 로컬 전용 최신본이다. 중간 파일은 /tmp에 두고 한글 추출·모든 글꼴 포함·전체 페이지 가독성을 검수해 공유한다. PDF 때문에 게임 검사를 다시 실행하지 않는다. 이하 T05 진행 중 기록보다 이 최종 상태가 우선한다.

## 2026-11-06 — T05 재개, 실제 최종 검증 진행 중

현재 main/기준 `2188120`에서 기존 미커밋 #6 구현을 재개했다. GitHub #1/#6 본문·댓글(없음), #6 Open, 선행 #5 병합/Closed와 관련 PLAN/GLOSSARY를 대조했다. 사용자는 필요한 실행 권한을 허용하고 확인 질문 없이 진행하도록 요청했다. 구현 범위와 현재 브랜치 로컬 커밋 지시를 유지하며 push/merge/PR/이슈 종료는 수행하지 않는다.

개별 제작·설치·화로 투입/회수·철 채굴·도구 전제조건과 직접/제공 요약, 공유 허용 레시피, 실제 진단 실행기·생성물 출처를 연결했다. 기존 CLI/RPC/후보·관측 지도·보행·활성 틱 실행을 재사용한다. 독립 Standards/Spec 검토와 실제 사전 실패를 바탕으로 가려진 작업대 왕복, 일부 제공 목표 완료, 비참나무 연료, 소비 중 드롭 수집, 늦은 설치/투입/회수 응답을 보완했다. 상세는 docs/reviews/issue-6.md 및 DECISIONS의 T05 기록이다.

최종 개발 검사: 전체 pytest **77 passed(18.49초)**, strict mypy **23파일 통과**, Node 문법·diff 공백 검사 통과. mock/scripted 검사이며 실제 게임 물리 근거와 구분한다. 이후 런타임 소스 변경 없이 실제 검증을 수행 중이다.

사전 원시: artifacts/issue-6/preflight-1은 sandbox 서버 잠금 실패, preflight-2는 응답 중단과 잔여 서버로 미완료, preflight-3은 잔여 소유권 충돌이다. preflight-2 잔여 bridge를 SIGTERM으로 정상 종료하고 서버 종료를 확인했다. preflight-4는 **빈 인벤토리/배치 자원에서 50결정·1,681틱·408.19초**에 실제 철 곡괭이를 제작했다. 원목4·조약돌11·철광석3 직접 획득, 작업대/나무·돌 곡괭이/화로/철 곡괭이 직접 제작 사건은 남았으나 화로 입력의 늦은 인벤토리 반영으로 직접 제련 출처가 누락돼 검사 도구는 실패했다. unverified/exit1이며 최종 성공으로 쓰지 않는다. 마지막 기준 C4 reset/observe·0틱·빈 인벤토리·체력20 복원은 통과했다. 투입/회수 갱신 확인·출처 연결을 수정하고 배포 bridge 회귀를 통과시켰다.

final-1은 시계63/63·고유/준비63·상태 동일/drift0 완료 후 정보 감사22장면까지 진행했으나 화로에서 RPC timeout(624.27초)으로 실패했다. 기준 C4 reset은 통과했다. 설치된 Mineflayer의 열린 창에서 플레이어 슬롯 재고를 갱신하는 구조를 확인했고 inventory()가 현재 창의 items()를 우선 읽도록 한 줄 수정했다. 설비 입력/출력을 보유량에 합치지 않는다. load_window/collect_window 배포 bridge 회귀 RED→GREEN, 전체77passed(18.48초)·mypy23파일 통과. 실제 furnace-preflight는 투입5+wait200+회수2=207틱·직접 제련1·목표완료·reset을 확인했다. 미인증 사전 결과는 최종 성공과 구분한다.

새 production/G2 설정은 관측을 동반한400틱 실행의 벽시계 지연을 수용하도록 RPC180초이며 활성400/12000틱 상한은 그대로다. final-2는 기존 schema60초 제한으로 서버 실행 전 설정 거부됐고 공개 CLI RED→GREEN으로 schema 상한도180초로 맞췄다. 현재 실제 실행은 `.tools/uv run --locked python tools/verify_t05.py --output artifacts/issue-6/final-3 clock information production boundaries g2`다. bridge 변경으로 새 fingerprint63 → 26장면 감사 → 제작 → 경계 → 자연G2를 실행하고 마지막 기준 C4 reset을 시도한다. 최종 결과는 아직 없다.

고정 자연 G2에서 직접 철광석3이 없으면 전체 T05 인수 조건 미완료로 표시하고 관리자 iron/production 성공으로 대체하지 않는다. 자연 snapshot·시드·시작점·하강/터널·모델/API/학습·연구 예산을 바꾸지 않는다. 보고서/가이드 PDF 두 개는 실제 최종 결과 확인 후 로컬 reports에 생성하며 보고서 때문에 게임을 다시 실행하지 않는다.

## 2026-11-05 — T04 재개, 남은 실제 검사 완료

사용자의 `continue`로 중지한 #5 보완을 재개했다. GitHub #1/#5 본문·댓글(모두 댓글 없음, Open), AGENTS/CONTEXT/관련 PLAN/GLOSSARY와 작업 트리를 확인했다. final-2 manifest의 모든 소스 hash가 일치하고 bridge·Node/Java runtime·snapshot·설정 fingerprint도 기존 인증 `a15976b0849d81fc6d48d4ef73635fc4dfc4a88ce30318b6c161eee70886c789`와 같아 완료한 **시계63/63을 반복하지 않았다**. 코드·테스트 변경 없이 이미 완료한 pytest **68 passed**, strict mypy **20파일 통과**, 독립 Standards/Spec 재검토 **각0건**도 유지했다. 이번 재개는 남은 실제 진단·저장 근거 재계산·문서/PDF·로컬 커밋 범위다.

실행: `UV_CACHE_DIR=.cache/uv .tools/uv run --locked python tools/verify_t04.py --output artifacts/issue-5-review-2026-11-05/resume-1 information macros`. 드라이버 exit0. 실제 결과는 다음과 같다.

|검사|최종 결과|
|---|---|
|확장 정보 감사|18장면 통과, exit0, 494.08초. 관측/이동/군집·회수와 독립 장착·드롭 wait·0후보·wait20/100/200 숨은 광석/용암 쌍 불변, 벽 개방 양성 대조 통과.|
|맨손 수집|1결정·81틱·직접1개 획득·목표 완료·exit0.|
|장착 후 수집|3결정·103틱·직접1개 획득·목표 완료·exit0.|
|실제 파손|3결정·51틱·목표 완료·exit0. 같은 step의 mined/tool_broken 보존 후 직접1개 회수.|
|완료 틱 위험|12결정·72틱, mined/observed_hazard 동시 보존. 목표 미완료·exit1은 예상 결과.|
|독립 드롭 대기|2회 wait·40틱·직접1개 회수·목표 완료·exit0. 관리자 준비71틱은 에피소드와 별도.|
|0후보|12회 실제 wait+failed·240틱·actor 제외. 목표 미완료·exit1은 예상 결과.|
|실제 취소/재선택|실제 상태 진전20+취소 대기20=40틱을 원 선택에 보존, actor 제외·trace_mask=0 뒤 재선택. 총121틱·1실행 결정·목표 완료. 전체 realtime 인증과 구분.|
|최종 복원|G1 reset/observe 일치, 활성0틱·빈 인벤토리·체력20. 검사·서버 프로세스 종료 확인.|

모든 최종 step/summary는 paused·pause_verified=true이며 actor 전이0이다. `resume-1/evidence-recomputed.json`에 시계/재개 manifest hash 일치·실제 step 틱 합계·목표/예상 실패·취소 원 선택·reset을 원시에서 재계산한 결과를 보존했다. `final-1`과 `final-2` 감사 중단, `macros-preflight` 미인증 결과와 자연 G1 사전 실패(12결정294틱 나무 미발견)를 최종 성공으로 바꾸지 않았다. 최종 장착/파손 소요량은 이번 실제 드롭 이동 결과이며 사전 수치로 대체하지 않았다.

한국어 보고서 `reports/issue-005-T04-report.pdf`(2쪽)와 코드 가이드 `reports/issue-005-T04-code-guide.pdf`(3쪽)를 이번 보완·최종 실제 결과·코드 함수/시작 줄/hash·Git/이슈 상태로 교체한다. 한글 추출·사용 글꼴 전체 포함/subset/Unicode·모든 페이지 렌더 가독성을 확인하며, 생성 중간 파일은 /tmp에만 둔다. reports는 Git 제외, 다른 티켓 PDF는 보존한다. 보고서 때문에 게임 검사를 다시 실행하지 않는다.

검증본은 기존 main 이력을 보존해 현재 브랜치의 로컬 커밋으로 마무리한다. **push·PR·merge·이슈종료/댓글은 수행하지 않으며 #5는 Open**이다. 관리자 실제 진단 성공은 자연 C4/다이아·모델 성능의 근거가 아니다. 실제 사망은 mock 주입만 확인했다. 전체 realtime 운용, 제작/제련/하강/터널, 모델/API/과금/PPO/본 학습/최종 평가/일반화는 미실행이고 PC180시간 예산을 재확정하거나 증액하지 않았다. 후속 #6/T05는 이번에 착수하지 않는다.

## 2026-11-05 — T04 보완, 사용자 요청으로 중지

main `9f9aca5` 대비 완료 틱 증거 유실·위조 stop_rule_id/임의 wait·중복 근거/명명/죽은 분기, 공개 진단·감사 범위와 재현 실행기를 보완했다. 전체 pytest **68 passed(16.60초)**, strict mypy **20파일 통과**, Node 문법·diff 검사 통과. 독립 Standards/Spec 수정본 재검토 남은 지적은 각 **0건**이다. 항목별 처리는 `docs/reviews/issue-5-review-fixes-2026-11-05.md`.

실제 맨손/장착/파손 수집·완료 틱 위험·독립 dropwait·0후보·실제 제어된 취소/재선택은 macros-preflight에서 확인했으나 새 인증 전이라 unverified/exit1을 유지했다. 자연 G1 사전 공개CLI는12결정294틱에 나무미발견이며 관리자 진단 성공과 구분한다. 최종 코드 **verify-clock63/63**, 고유63/준비63/위치 drift0.0 재계산은 완료했다.

사용자가 내일 continue하도록 중지를 요청해 정보 감사를 SIGINT로 중단했다. `artifacts/issue-5-review-2026-11-05/final-2/`에 clock exit0·audit exit-2/미완료(요약 없음)·G1 reset/observe 일치·0틱·빈 인벤토리·체력20 복원을 기록했고 검사/서버 프로세스 종료를 확인했다. 중단 뒤 driver AssertionError는 의도한 중단의 종료코드 검사이며 감사 완료나 새 결함으로 세지 않는다. final-1도 준비 틱 집계 수정 전 중단/복원 기록이다.

현재 **미커밋·미푸시**, PR/merge/이슈종료 없음. 확장 감사18장면·인증 후 최종 공개CLI/macros·최신 PDF 생성/검수·로컬 커밋이 남았다. reports의 #5 두 PDF는 이전 판본이며 교체하지 않았다. 재개 명령과 상세 상태는 `CONTEXT.md`에 보존했다. continue 전에는 추가 작업을 실행하지 않는다.

## 2026-11-04 — 이슈 #5 / T04 원목 후보·채굴·획득

기준: 시작 시 깨끗한 main `e60493612125ea8803e533838acefc089005f818`, GitHub #1/#5 본문·댓글(둘 다 댓글 없음), PLAN §§4.1–4.3/5.2/5.4/12–14, GLOSSARY. #2–#4는 Closed이므로 선행 조건을 충족했고 다음 티켓은 #5임을 확인했다. `implement` 지시에 따라 현재 main에 구현·검증 변경을 로컬 커밋한다. push·merge·PR 생성·#5 종료는 실행하지 않으며 GitHub #5는 Open이다.

### 구현

- 공개 `smoke-macros`, mock pilot과 실제 G1 `configs/macros.yaml`. 제한 관측의 현재 노출 원목·같은 높이 접근 경로·장착·1/최대 8블록 작업량을 중복 제거해 최대 8후보로 저장한다. ID·내용·순서·mask·source obs/map과 결정별 macro_steps를 보존한다.
- 기존 보행/정지와 실제 활성 틱 기반 채굴 패킷, 서버 파괴 확인·직후 2틱 내 드롭 생성·자기 수집·인벤토리 증가 연결. 선택 밖 군집으로 확장하지 않는다. 노출 군집 최대 8블록/400틱, wait 20/100/200틱, 매 기본 조작 관측과 위험·피해·산소·파손·실패·시간·사망 중단을 연결했다.
- 0후보 실제 wait+failed, 1후보 확률 1과 actor 제외. 취소된 원 후보/선택·대기 사건/시간·비용을 보존하고 trace_mask=0 뒤 재선택한다. 미실행 매크로 상한과 취소 대기를 구분하고 사건 ID의 중복 집계를 거부한다. smoke actor 전이는 항상 0이다.
- 실제 회수 실패를 추적해 기존 정지 확장이 클라이언트 이동 패킷을 버려 서버 플레이어는 출발점에 남는 결함을 확인했다. 서버 스레드에서 최신 위치/방향을 보관하고 활성 틱에 vanilla 검증으로 적용하며 순서·텔레포트 경계를 보완했다. 이동 종료에서 서버/클라이언트 위치도 0.001블록 이내로 일치해야 한다. 관리자 위치는 검증에만 사용한다.
- 정지 중 공중 상태의 벽시계 비행 추방을 막도록 표준 allow-flight=true를 공통 서버 설정으로 고정했다. Survival 비행 능력/물리·행동 권한은 바꾸지 않는다. backend 시작 전에 검사하고 fingerprint에 포함한다. 자체 확장 jar SHA-256은 `83d8fdc54807e788087c4800298d8f3da46e803ad76a65e0632614dcd5ffcfc8`이다.

### 검증

- 새 CLI·후보/단일 확률·0후보, 관측 드롭 회수·실제 위치 기준 회수 거리, 취소 20/450틱·짧은 취소 상한, 중복 사건, 현재 시야/중복 제거/8후보, 오래된·실패한 파괴 출처, 위치 불일치 거부를 공개 CLI/배포 bridge로 검사했다. 회귀는 RED→GREEN을 확인했다.
- 최종 전체 pytest **65 passed(16.32초)**, strict mypy **19개 파일 통과**, Node 문법·diff 공백 검사 통과. 실제 Java 소스를 설치된 jar와 컴파일한 5개 패킷 순서/정지/텔레포트 assert도 통과했다. mock/scripted 검사는 실제 물리 근거가 아니다.
- 독립 code-review: Standards 1건, Spec 2건을 재현·수정했다. 추가 Java 경계 검토의 패킷 순서 2건도 재현하고 5개 assert로 수정 검증했다. 상세는 docs/reviews/issue-5.md.
- 최종 실제 서버 이동 사전 검사: **2결정·47틱**, 정상 경로 완료, 각 이동 종료의 서버/클라이언트 위치 일치 검사 통과. 이 사전 검사 당시에는 새 인증 전이라 unverified를 유지했다.
- 최종 실제 verify-clock: **63/63 통과**, 낙하 10초 사전 검사도 통과. 새 Java 확장·bridge·allow-flight 설정 fingerprint로 인증했다.
- 실제 audit-information: **통과, 148.19초**, 현재 관측·보행·원목 군집 채굴·드롭 회수 범위. 숨은 광석/용암 입력 쌍은 일치하고 이동은 각각 **18틱**, 목재 군집은 각각 **156틱·원목 2개 직접 획득·정지 인증/안정 경계 true**로 일치했다. 벽 개방 양성 대조도 통과했다. 무작위 드롭 좌표·사건/entity ID만 정규화하고 정책 상태·item/count·경로·중단 근거는 비교했다.
- 실제 맨손 수집: **2결정·162틱·직접 2개 획득**. 도끼 장착 포함: **3결정·103틱·직접 2개 획득**. 모두 goal_completed=true, paused/인증 true, actor 0, 진단 보상 2.0이다. 용암 위험에서 **1틱·observed_hazard·stable_boundary=false**를 확인했다.
- 진단 뒤 **기준 G1 snapshot reset/observe 일치·0틱·빈 인벤토리·체력 20**을 확인하고 서버를 종료했다. 진단 지형을 자연 task snapshot으로 저장하지 않았다. 최종 raw는 `artifacts/issue-5/final-4/`, 실행기/패킷 재현 검사는 `artifacts/issue-5/`에 보존한다.

### 실패와 해석·상태

샌드박스의 서버 소유권 잠금 차단은 권한 재실행과 구분했다. 최초 probe는 2개 중 1개만 회수(271틱)해 실패했고 수정했다. 해당 최초 JSONL은 두 번째 probe에 의해 교체됐으므로 도구 출력의 실패 요약을 별도 JSON으로 남겼고 이후 final-1~4 원시는 분리 보존했다. final-1은 시계 63회 통과 후 목재 감사/회수에 실패했다. 진단 위치 대조에서 client `[-239.5597,100,187.7220]`, server `[-240.5,100,186.5]`를 확인해 실제 이동 결함을 수정했다. final-2 사전 검사는 정상 이동을 unverified 때문에 실패로 판정한 실행기 조건을 보완했다. final-3은 서버 이동 통과 후 시계 37회 지점에서 낙하의 floating 자동 추방으로 중단됐으며 공통 설정을 수정하고 final-4에서 63회 전체를 다시 통과했다. 이전 클라이언트 보행 성공만으로 실제 서버 이동을 입증했다고 해석하지 않는다.

실제 원목은 관리자 진단용 배치다. 자연 C4/다이아 성공이나 학습·모델 성능 결과가 아니다. 실제 realtime 전환·제작/제련/하강/터널·7B/NanoJev/Jev/Astra·과금·PPO·본 학습·최종 평가·일반화는 미실행이며 PC 180시간의 충분성을 재확정하거나 증액하지 않았다. 다음 티켓은 #6/T05다. 보고서 작성 때문에 게임 검사를 추가 실행하지 않는다. `reports/issue-005-T04-report.pdf`, `reports/issue-005-T04-code-guide.pdf` 두 개를 로컬 전용으로 생성했다. 각각 A4 2쪽이며 한글 추출·모든 사용 글꼴 embedded/subset/Unicode mapping·전체 4페이지 가독성 검수가 통과했다. HTML/중간 파일은 /tmp에만 두고 PDF는 Git 추적·커밋에서 제외한다.

## 2026-11-04 — 리뷰 수정본 재검토 후 사망 경로 결함 수정

수정본 재검토(Standards/Spec)에서 이전 지적은 모두 해소됐고 새 결함 1건이 확인됐다. 거부된 이동 경로도 bridge가 1틱을 실행하므로 그 틱에 사망하면 `invalid=false`, `path=[]`인데 episode의 이동 근거 검사가 후보 경로를 기대해 사망을 `invalid_step`으로 바꿨다. 기대 경로를 `invalid` 또는 `reason=invalid_path`일 때 빈 경로로 판정하도록 고쳤다. 공개 CLI 회귀 `test_movement_death_during_rejected_path_tick_stays_terminal`이 수정 전 실패(invalid_step)·수정 후 통과함을 확인했다. 전체 pytest **55 passed**, mypy·diff 공백 검사 통과. Python 검사 한 줄만 바꿨고 bridge는 변경하지 않아 실제 Minecraft 재실행은 하지 않았다. 남은 판단 사항(이동 근거 검사의 episode/information 중복, MovementEvidence 필드 재선언)과 결정당 약 1.2초의 경계 확인 지연은 T19 예산 실측에서 다룬다.

## 2026-11-04 — 로컬 보고서 폴더 정리

사용자 요청으로 reports에는 #2/T01 최종본, #3/T02·#4/T03 최신 v2의 보고서/코드 가이드 PDF 한 쌍씩 총 6개만 유지한다. 나머지 이전 PDF·통합 리뷰 PDF·HTML·README·템플릿·CSS·patch는 삭제한다. 남긴 PDF는 내용 변경 없이 보존한다. 기존 보고서 보존·HTML 동봉 규칙은 이번 명시적 요청으로 대체하고 AGENTS를 갱신했다. reports를 .gitignore 및 Git 추적 제외 대상으로 변경하며 새 보고서·코드·게임 검사는 만들거나 실행하지 않는다. 기존 Git 이력은 재작성하지 않으며 commit/push는 수행하지 않는다.

## 2026-11-04 — T01–T03 로컬 리뷰 지적 재현·수정

사용자가 작업 폴더의 `code-review-2026-11-04.txt` 지적을 실제로 검증하고 맞으면 고치도록 요청했다. main `893ff27`에서 #1 본문·댓글(없음), #3/#4 본문·댓글(없음), PLAN §§4.1–4.3/5.2/12–14와 GLOSSARY를 대조했다. 시작 때 이미 존재한 PROGRESS/보고서 README/TEMPLATE 변경과 code-guide HTML/PDF, 원문 리뷰는 보존했다. 현재 수정은 미커밋·미푸시이며 새 PR·merge·GitHub 게시/이슈 변경은 수행하지 않았다. #2/#3/#4는 조회 시 이미 Closed였다.

### 재현과 구현

- 실제 Mineflayer 4.39.0의 error forwarding을 쓰고 네트워크 client만 대체한 주입 검사에서 stdout의 여러 줄 Error로 JSON 파싱 실패를 재현했다. logErrors=false로 끄고 연결 오류는 민감한 원문 없이 stderr에 남긴다.
- 인증 없는데 paused로 반환하는 경로를 수정했다. StepResult는 paused↔pause_verified 일치를 강제하며 미인증 실제 결과는 unverified다. summary에도 pause_verified를 남기고 에피소드 중 모드 불일치·오류를 마지막 정상 step으로 덮지 않는다. 실제 미인증 smoke는 exit 1이다.
- 기존 인증서가 매 결정의 실제 정지 확인을 대체하던 공백을 보완했다. reset·wait/이동 종료에서 입력 해제/클라이언트 물리 정지 후 양쪽 전체 상태 두 표본과 실제 틱의 불변을 확인한다. freeze 요청을 보냈으면 깊은 정지 응답도 검사한다. 변화·거부 시 인증 해제/backend_error다. 관리자 player 표본은 시계 검사에만 사용한다.
- 이동 summary의 movement_steps에 결정별 후보 ID·원본 obs·map·사건·path/stop 근거·이유·시간·거리·안정 경계를 남긴다. 잘못된 source_obs_id/map_version/path/stop_evidence와 빈 events가 성공 처리되던 다섯 변형을 공개 CLI에서 invalid_step으로 거부한다.
- 실제 backend 필요 오류는 exit 2/invalid_config를 유지하고 원인과 configs/minecraft.yaml을 안내한다. AGENTS의 잘못된 감사 설정 예시를 고쳤다. vec3 0.1.10 직접 의존성/lock 선언, 항상 참인 payload 검사 제거, 전체 bridge 로드로 물리 fixture의 함수 순서 의존성도 제거했다.
- 단순 중복 틱/안전 검사·과제/장면/권한 목록·63 상수·private RPC 호출은 현재 기능 불일치가 없어 구조를 유지했다. README에 uv PATH 설정이 이미 있으므로 영구 셸 변경은 하지 않았다. 전체 판정은 `docs/reviews/review-fixes-2026-11-04.md`, 선택 이유는 DECISIONS에 기록한다.

### 개발 검사

변경 전 pytest **38 passed(9.90초)**. Python 회귀 12개 RED→GREEN, Mineflayer 오류/경계 drift·freeze 거부 5개 RED+정상 대조 1개→모두 GREEN을 확인했다. 미인증→인증/인증→미인증의 두 다중 결정 회귀도 추가했다. 최종 전체 pytest **54 passed(13.78초)**, strict mypy **16개 파일 통과**, Node 문법·git diff --check·npm ls vec3 통과다. 기존 scripted 물리의 거리 상한·얼음 거부·실패 1틱 변위를 유지했다. 독립 읽기 전용 코드 검토에서 추가 구체적 결함은 없었고 검토자도 주입 시나리오/물리 fixture를 재실행했다. scripted 검사를 실제 정지 근거로 표시하지 않는다.

### 실제 Minecraft 재검증 (2026-11-04)

- sandbox 최초 smoke는 서버 디렉터리 flock 제한으로 backend_error였고, 권한 재실행과 별도로 보존했다. 실제 미인증 smoke는 **exit 1**, 2결정·40틱·14.30초, step/summary 모두 **unverified/false**, error=null이다. 새 코드와 다른 과거 인증을 재사용하지 않았다.
- 새 공개 verify-clock은 **exit 0, 63/63**, 63개 고유 조합·위험 장면 준비 63/63·양쪽 위치 최대 drift **0.0**, 다른 상태·사건·틱 불변이다. 새 코드/package-lock fingerprint로 실제 다시 인증했다.
- 인증 후 공개 smoke-episode는 **exit 0**, 2결정·40틱·14.19초, **paused/pause_verified=true**다. 실제 wait이며 원목 획득·학습 결과가 아니다.
- 공개 smoke-movement는 **exit 0**, **2결정·47틱·6.37928897648239블록·21.03초**, movement_completed=true, paused/인증 true다. 두 결정의 사건/원본 obs/map/이유/시간이 최종 movement_steps에 남았다. actor 0·보상 0·다이아 성공 false, 정상 decision_limit 절단이다.
- 공개 audit-information은 **exit 0, information_verified=true, 57.43초**다. 숨은 광석/용암 두 장면의 공개 입력 hash는 모두 `7c35ab78e49d07ccd3a42abb987471f493db1acb65147cddb88f554e4e4dc38d`이며 셀 1,161개·후보 8개다. 두 이동은 모두 **18틱·2.1548446042413616블록·path_completed·지도 버전 6·정지 인증/안정 경계 true**로 같다. 벽을 연 두 양성 대조도 통과했다.
- 진단 뒤 C4 기준 snapshot reset/observe 일치, 활성 틱 0·빈 인벤토리·체력 20을 확인하고 서버를 종료했다. 자연 snapshot을 덮어쓰지 않았다. 모든 시도/검사·복원 근거는 `artifacts/review-2026-11-04/`에 저장했다.

기존 같은 이동 17.63초 대비 이번 21.03초는 추가 경계 확인의 벽시계 비용을 포함한다. 활성 틱/거리는 같지만 처리량 보장은 아니며 본 학습 전 예산을 새로 실측해야 한다. 현재 180시간을 충분하다고 재확정하거나 늘리지 않는다. 모델·PPO·유료 API·본 학습·최종 평가·새 월드 일반화·자연 다이아 성공은 미실행/미검증이며 새 의존성 다운로드·결제는 없다.

후속 보고서는 `reports/issue-003-004-T02-T03-2026-11-04-review-fixes.{html,pdf}`다. A4 **3쪽**, 한글·핵심 수치 추출과 세 글꼴 embedded/subset/Unicode mapping을 확인하고 모든 페이지 이미지를 직접 읽었다. 잘림·깨짐·표 행 분리·외딴 문장 페이지가 없다. WeasyPrint fontTools fallback 경고는 출력/가독성 실패가 아니며 새 시스템 패키지는 설치하지 않았다. 현재 코드는 미커밋이므로 원격 링크는 고정 main의 수정 전 비교 위치임을 명시하고, 실제 변경본은 신규 fixture까지 포함한 동봉 `.patch`로 보존했다. patch SHA-256 `ed5117837573387b7739c18103c0e315b94d61b0e9a848e6d46cc082f5114a67`, `git apply --reverse --check` 통과다. 기존 보고서와 사용자 문서 변경을 보존했으며 최종 프로세스 목록에 Minecraft/Java 서버가 남아 있지 않다.

## 2026-11-03 — 보고서별 핵심 구현 코드 안내 추가

사용자 요청으로 이슈 #2/#3/#4의 기존 보고서 5개 각각에 핵심 변경·구현 → 파일·함수/클래스·시작 줄 → 확인할 로직 표와 권장 읽기 순서를 추가한 `-code-guide.{html,pdf}` 판본을 만들었다. 기존 HTML/PDF는 바이트까지 보존했다. 코드 링크는 원문 범위에 맞춰 각각 d809cd9 / 1312252 / 21a6359 / 0b92880 / ad2790b에 고정했다. 최신 main의 후속 기능을 과거 구현으로 혼동하지 않도록 기준을 명시했다. reports/README.md에 5개 추가본 링크와 작성 규칙을, TEMPLATE.html에 같은 코드 안내 항목을 반영했다.

검증: 코드 링크 **77개** 모두 로컬 Git에서 해당 커밋의 파일·시작 줄/정의를 확인했고 PDF의 URL annotation에도 남아 있음을 확인했다. 새 PDF는 각각 3/4/3/3/3쪽(총 16쪽)이다. 한글 추출·모든 글꼴 포함/subset/Unicode mapping 통과. 기존 본문 11쪽은 텍스트와 페이지 이미지가 원본과 같음을 비교했다(전체 쪽수 표시가 달라지는 푸터 제외). 추가 코드 안내 5쪽은 직접 이미지를 읽어 잘림·깨진 글자·표 행 분리·외딴 문장 페이지가 없음을 확인했다.

문서와 보고서만 변경했다. pytest/mypy·실제 Minecraft·모델·학습은 재실행하지 않았으며 기존 수치를 새 실행 결과로 표시하지 않았다. 현재 변경의 commit·push는 수행하지 않았다.

## 2026-11-03 — PR #29 수정본 실제 재검증 완료

수정 코드 `ad2790b`를 `origin/ticket-4`에 푸시했다. Standards의 P2 두 건을 재현·수정했고 수정본 독립 재검토는 남은 중대한 문제 없음, Spec도 남은 차단 지적 없음이다. GitHub 계정의 approve 리뷰로 표시하지 않는다.

- 수정본 공개 verify-clock은 **exit 0, 63/63 통과**다. backend/terrain 변경으로 무효화된 과거 인증을 사용하지 않고 새 코드 fingerprint로 실제 다시 검사했다.
- 공개 audit-information은 **exit 0, information_verified=true, 46.63초**다. 숨은 두 경우의 공개 셀 1,161개·후보 8개·입력 hash `7c35ab78e49d07ccd3a42abb987471f493db1acb65147cddb88f554e4e4dc38d`와 실행/중단 결과가 같다. 두 이동 모두 **18틱·2.1548446042413616블록·path_completed·정지 인증/안정 경계 true**다. 벽을 연 두 양성 대조에서 해당 광석/용암을 관측했다.
- 자연 지형 smoke-movement는 **exit 0, movement_completed=true, 2결정·47 활성 틱·6.37928897648239블록·17.63초**다. 두 step 모두 path_completed·pause_verified=true·stable_boundary=true. actor 0·보상 0·다이아 성공 false이며 decision_limit 절단이다.
- 마지막 C4 기준 reset 후 active_ticks=0·빈 인벤토리·체력 20·reset/observe 일치를 확인하고 서버를 종료했다. 수정본 검사 코드와 raw artifact는 기존 파일을 덮지 않고 `artifacts/issue-4/pr29/`의 `final-check-pr29.py`, `verify-clock.jsonl`, `audit-information.jsonl`, `smoke-movement.jsonl`, `restore.json`, `final-checks.json`에 저장했다.

최종 코드의 전체 pytest **38 passed(9.96초)**, strict mypy **16개 파일 통과**, Node 3개 파일 구문·공백 검사 통과다. 임시 검증 스크립트를 같은 이름으로 복사해 mypy의 Duplicate module 오류가 발생한 것은 검증 파일명을 `final-check-pr29.py`로 구분해 해결했고 재실행이 통과했다. 제품 설정/의존성은 바꾸지 않았다.

기존 보고서를 보존하고 검토·수정·새 실제 재검증과 Git 상태를 `reports/issue-004-T03-2026-11-03-v2.{html,pdf}`에 기록했다. A4 2쪽의 한글/수치 추출·모든 글꼴 포함/subset/Unicode mapping과 두 페이지 이미지를 직접 확인했으며 잘림·깨진 글자·표 분리·문장만 남은 페이지가 없다. 최종 기록을 같은 PR에 반영한다. PR #29는 Open이며 main 머지·이슈 #4 종료는 수행하지 않는다. 얼음류 보행은 실제 제동 교정 전까지 제외하며 채굴·제작·계단·터널·모델/API·학습은 미실행이다.

## 2026-11-03 — 이슈 #4 PR #29 생성·독립 검토 수정

구현·문서·원본 보고서 18개 파일을 `0b928808b6f5855b754219a23ca0a920d66dfc58`로 커밋하고 `origin/ticket-4`에 푸시했다. [PR #29](https://github.com/sion0507/Minecraft_RL/pull/29)를 생성했으며 원격 head 일치·base main `624b9c6`·MERGEABLE·Open, 원격 statusCheckRollup 비어 있음을 확인했다. PR 본문에 실제와 mock/scripted 검증을 구분하고 #4를 연결했다. main 머지·이슈 종료는 수행하지 않는다.

두 독립 검토자의 Standards/Spec 검토를 수행했다. Standards에서 P2 두 건을 재현했다. (1) 얼음 관성으로 이동 상한 16블록을 넘는 경우: ice/packed/frosted 16.8120, blue_ice 17.0373블록. 네 종류는 관측하되 제동 교정 전까지 support=false로 제외한다. (2) 무효 경로의 필수 1틱에서 실제 0.1블록 움직였지만 거리 0·stopped로 기록하는 경우: 중복 tick 처리를 합쳐 실제 변위를 기록한다.

설치된 Physics/PlayerState와 실제 Terrain 관측을 쓰는 scripted fixture에서 첫 상한 초과 RED, 수정 후 실패 tick 거리 RED를 차례로 확인한 뒤 전체 pytest **38 passed(9.96초)**·strict mypy **15개 파일**·Node 3개 파일 구문·diff 공백 검사를 통과했다. 이 fixture는 실제 서버 검증이 아니다. 돌/슬라임은 각각 15.3222/15.8764블록으로 상한 안이며 얼음 네 종류는 경로를 거부하고 실패 1틱의 변위는 실제 0.1블록과 일치한다.

수정본 재검토에서 Standards 두 건 해결·남은 중대한 문제 없음, Spec 남은 차단 지적 없음이다. 사용자 요청에 따라 수정 commit을 같은 PR에 푸시하고 실제 정지 인증·정보 감사·이동을 새 코드로 재검증한다. 이 문단 작성 시 실제 재검증은 진행 중이며 완료를 주장하지 않는다. 과거 보고서와 raw artifact는 보존한다.

## 2026-11-03 — 이슈 #4 커밋·푸시·PR 검토 준비

사용자가 이슈 #4의 커밋·푸시·PR 생성과 검토를 요청했다. `ticket-4`와 최신 `origin/main`의 공통 기준은 `624b9c6`이다. 이슈 #4는 Open이며 기존 ticket-4 PR은 없고 최신 #1/#4 본문·댓글을 재조회했다. 실제 코드·보고서·문서만 커밋하며 월드/원시 artifact/캐시를 제외한다. 기존 PDF/HTML의 작성 당시 미커밋 상태는 보존한다.

직전 전체 pytest **37 passed(9.65초)**, strict mypy **15개 파일 통과**, Node 두 파일 구문·diff 공백 검사 통과. 코드/게임 환경을 바꾸지 않았으므로 기존 실제 정지 63/63·이동·정보 감사를 이 단계에서 불필요하게 재실행하지 않는다. PR 검토에서 런타임을 바꾸면 정지 인증과 실제 검증을 다시 확인한다. main 머지·이슈 종료는 이번 요청에 포함하지 않는다.

## 2026-11-03 — 이슈 #4 / T03 제한 관측·이동·정보 감사 완료

사용자 요청으로 다음 티켓을 확인했다. #2/T01과 #3/T02는 Closed이며 #3은 PR #28로 main에 머지됐다. main `624b9c6`에서 `ticket-4`를 생성했다. 샌드박스의 Git ref 쓰기 제한 후 승인된 재실행으로 브랜치를 만들었다. GitHub #1/#4 본문·댓글(댓글 없음), PLAN §§4.1–4.3/5.2/12–14와 기존 실행기를 기준으로 구현했다. 현재 변경은 미커밋·미푸시이며 PR 생성·main 머지·이슈 #4 종료는 수행하지 않았다.

### 구현

- `bridge/terrain.js`는 눈 위치에서 반경 8블록 셀 중심으로 광선을 보내 처음 충돌 표면/위험에서 중단한다. 통과한 공기·비충돌 식물과 직접 보인 표면·관측 지도·방문/최근 결과만 저장하고 reset마다 비운다. 미로딩 셀을 통행 지도로 넣지 않고 시드·관리자 상태·전체 청크·숨은 블록을 후보/경로/중단에 제공하지 않는다.
- 공개 지도 BFS로 같은 높이의 바닥·발/머리 공간을 연결해 최대 8개·16블록/400틱의 보행 후보를 만든다. Node도 원본 obs/map과 경로 연속성·공개 전제조건을 검증하며 각 기본 이동 뒤 관측을 갱신한다. 공개 위험·피해·길 변경·정체에서 중단하고 정상 종료는 입력 해제 후 공개 지면·수평 정지를 확인한다. 보행 중 클라이언트 물리도 서버 실제 틱 수만큼만 실행한다.
- 기존 공개 episode 흐름에 `smoke-movement`를 추가했다. moved/stopped 사건, source obs·map 버전·경로·중단 근거·틱·거리·경과 시간을 기록하고 안정된 경로 완료가 없으면 exit 1이다. RPC 시작 오류를 실제 mock 시계로 표시하지 않고 unverified로 구분한다.
- `audit-information`은 관리자 전용으로 진단용 벽 뒤 광석/용암 장면을 준비하고 일반 정책 observe/step으로 비교한다. run ID·벽시계만 제외해 관측·후보·경로·실행/중단 근거의 일치를 요구하고, 벽을 연 양성 대조에서 노출도 확인한다. 관리자 준비 데이터를 정책 관측에 섞지 않는다. 실제 정지 인증·최대 틱·거리·사건 출처·관측/지도/경로 근거도 검사한다. 자연 snapshot은 보존한다.

### 실제 Minecraft 검증 (2026-11-03)

- 공개 `verify-clock`: **exit 0, 63/63 통과**, 위치 허용 오차 0.001블록. 평지·제련·드롭·용암·낙하·침수·화염의 0/5/10초 각 3회다. 변경된 backend/terrain을 포함한 새 fingerprint로 인증했고 과거 인증을 재사용하지 않았다. 원시 근거 `artifacts/issue-4/verify-clock.jsonl`.
- 공개 `audit-information`: **exit 0, information_verified=true**, 46.71초. 숨은 두 장면은 노출 전 각각 공개 셀 1,161개·후보 8개이고 입력 SHA-256 `7c35ab78e49d07ccd3a42abb987471f493db1acb65147cddb88f554e4e4dc38d`가 같다. 두 실행 모두 **18틱·2.1548446042413616블록·path_completed·안정 경계**, 지도 버전 6이며 관측·경로·사건·중단 근거가 정확히 같았다(벽시계 제외). 벽을 연 광석/용암 장면은 각각 공개 셀 1,175개에서 해당 대상을 직접 관측했다. `hidden_hazard_peek=false`; 실제 관리자 진단 장면이며 자연 광석 성공이 아니다. 원시 근거 `artifacts/issue-4/audit-information.jsonl`.
- 최종 공개 `smoke-movement`: **exit 0, movement_completed=true**, 2결정·47 활성 틱·총 6.37928897648239블록·17.56초. 두 step 모두 path_completed·pause_verified=true·stable_boundary=true. 각각 15/32틱, 지도 버전 12/42다. actor 전이 0·보상 0·다이아 성공 false이며 유효 decision_limit 절단이다. 원시 근거 `artifacts/issue-4/smoke-movement.jsonl`.
- 진단 뒤 C4 기준 snapshot으로 다시 reset했다. 활성 틱 0·빈 인벤토리·체력 20과 reset/observe 일치를 확인하고 서버를 정상 종료했다. 진단 장면을 현재 월드로 남기지 않았다. 검사 코드/근거: `artifacts/issue-4/final-check.py`, `restore.json`, `final-checks.json`.

### 실패·수정·독립 검토

최초 sandbox 실행은 서버 소유권 확보 실패였고 승인된 실제 장비 실행으로 재검증했다. 첫 실제 이동은 풀을 불투과 셀로 분류해 발밑 지면이 누락되어 중단됐다. 공개 관측으로 원인을 확인하고 비충돌 식물은 통과하도록 고쳤다. 다음 시도는 접지 중의 정상 `vy=-0.0784000015258789`를 이동으로 오인해 안정화가 끝나지 않고 RPC timeout이 발생했다. 실제 T02 기록·설치 물리 코드를 대조하고 접지·수평 정지 판정을 RED→GREEN으로 고쳤다. timeout 시도는 완료된 step이 없어 부분 활성 틱을 확정값으로 주장하지 않으며 actor 경험은 없다. 실패/중간 결과 `movement-attempt-1.jsonl`, `movement-attempt-2.jsonl`, `movement-before-final-check.jsonl`을 보존했다.

별도 읽기 전용 코드 검토에서 3축 광선 동률의 뒤 모서리 조회 결함을 재현했다. 첫 차단에서 즉시 반복을 중단해 숨은 셀 조회 7회→0회로 고쳤다. smoke가 대기/불안정만으로 성공하는 문제와 죽은 플레이어의 physicsTick 대기도 보완했다. 수정본 독립 재검토는 남은 중대한 문제 없음이다. 후속 자가 검토로 감사의 동일한 401틱 응답 허용을 RED→GREEN으로 수정했다. 검토 상세 `docs/reviews/issue-4.md`.

전체 pytest **37 passed(9.66초)**, strict mypy **14개 파일 통과**, Node 두 파일 구문·diff 공백 검사 통과. 모의/transport 검사는 실제 물리 근거와 구분한다. 검토 PDF·HTML을 `reports/issue-004-T03-2026-11-03.{pdf,html}`에 저장했다. PDF는 A4 2쪽이며 한글/핵심 수치 추출·모든 글꼴 포함/subset/Unicode mapping을 확인했다. 두 페이지를 PNG로 렌더링해 직접 읽었고 잘림·표 분리·깨진 글자·문장만 남은 페이지가 없다. WeasyPrint의 fontTools fallback 경고는 있었으나 출력/가독성 검사는 통과했다. 기존 보고서는 보존했다.

### 제한과 다음 작업

현재 보행은 같은 높이의 확인된 온전한 지면만 다루며 유리/부분 충돌 표면은 보수적으로 시야를 가린다. 일반 높이 차·점프·채굴·제작·계단·터널, 모델/API·PPO·전체 C4/G4 평가·온라인 인증은 미실행이다. 후속 제작/하강/터널 감사는 담당 티켓과 최종 lock 전에 추가한다. 새로운 월드 일반화·자연 다이아 성공·행동 모델 성능을 주장하지 않는다. 새 의존성·모델 다운로드·학습·유료 호출·결제는 없다. 다음은 #5/T04 관측 원목 직접 수집이다.

## 2026-11-03 — PR #28 수정본 검토·실제 재검증 완료, 통합 준비

리뷰 수정 코드 `21a63593992eb0b51630a1110c535ed83f85de51`을 `origin/ticket-3`에 푸시했다. 두 독립 검토자는 수정 diff를 재검토해 Standards 남은 차단 문제 0건, Spec 추가 차단 문제 0건으로 판정했다. Spec의 실제 재검증 조건도 아래 실행으로 충족했다. GitHub 계정의 승인 리뷰로 표시하지 않는다.

수정본 공개 verify-clock은 **exit 0, 63/63**이다. 63개 고유 조합 모두 위험 장면 준비 상태를 만족하고 before/after 측정값이 정확히 같으며 위치 drift 0, 낙하 9건 모두 공중 상태다. 원시 결과 `artifacts/issue-3/verify-clock-pr28.jsonl`, 새 인증 fingerprint `d9aeb6f565cea776a90a4be6912835e2a93c2553520cfb38395af67e231aca50`. 과거 인증을 새 코드의 근거로 재사용하지 않고 실제로 다시 검사했다.

후속 공개 실제 smoke도 **exit 0, 2결정·40틱·10.97초**, 두 step pause_verified=true, actor 0·보상 0·다이아 성공 false, 정상 decision_limit 절단이다. reset 뒤 새 인증 재사용을 확인했고 CLI가 서버를 종료했다. 원시 결과 `artifacts/issue-3/smoke-episode-pr28.jsonl`. pytest 29개·mypy 12개 파일과 Node/공백 검사는 코드 수정 후 통과한 결과이며 문서 작성 중 불필요하게 다시 실행하지 않았다.

후속 PDF는 A4 2쪽으로 출력해 모든 페이지 이미지를 직접 확인했다. 한글·핵심 수치 추출, 전체 글꼴 embedded/subset/Unicode mapping, 잘림·표 분리 없음도 확인했다. 기존 PDF/HTML을 보존하고 `reports/issue-003-T02-2026-11-03-v2.{html,pdf}`에 독립 검토·수정·새 실제 검증·미실행과 작성 당시 Git 상태를 구분해 기록한다. 이 기록 작성 시 PR #28은 Open, main 미머지·이슈 #3 Open이다. 검토 문서/보고서를 같은 PR에 반영한 후 요청대로 merge하고 종료 상태를 확인한다. 최종 통합 상태는 PR/이슈의 GitHub 기록을 따른다. 모델/PPO·유료 API·전체 예산 검증을 수행하거나 완료로 주장하지 않는다.

## 2026-11-03 — PR #28 독립 검토와 정지 인증 보완

사용자 요청으로 `ticket-3`→`main` PR [#28](https://github.com/sion0507/Minecraft_RL/pull/28)을 생성했다. 기준 main `1de47b7`, 최초 검토 head `29c962d`다. 별도 읽기 전용 Standards/Spec 검토를 병렬 수행했다. Spec은 T02 범위에서 추가 차단 지적이 없었다. Standards는 Fabric Loader/Mixin/intermediary/ASM 및 실제 remapped game jar가 fingerprint에서 빠져, 의존성 변경 후 옛 정지 인증을 재사용할 수 있는 P2를 발견했다.

서버의 `.fabric/`, `libraries/`, `mods/` 전체 트리와 bootstrap/game jar를 실제 내용으로 hash하도록 보완했다. 기존 snapshot treeHash를 재사용하고 추가 모드도 hash 변화에 포함한다. 회귀 검사는 누락된 메서드에서 먼저 실패한 뒤 변경·원복·모드 추가의 hash 동작을 통과했다. 기존 drift 검사 fixture가 미준비 상태여서 실패 이유를 구분하지 못하던 부분도 준비된 샘플과 무변경 성공 대조군으로 고쳤다. 이 scripted 검사는 물리 근거가 아니다.

수정 후 전체 pytest **29 passed(9.23초)**, strict mypy **12개 파일 통과**, Node 구문·diff 공백 검사 통과다. 새 fingerprint로 실제 공개 63회 정지 검증을 실행 중이며 `artifacts/issue-3/verify-clock-pr28.jsonl`에 저장한다. 이 시점 실제 재검증·수정본 독립 재검토·main 머지·이슈 종료는 미완료다. 기존 보고서는 보존하고 최종 결과는 별도 후속 PDF/HTML에 기록한다.

## 2026-11-03 — ticket-3 구현 커밋·원격 푸시 완료

구현·설정·검토 문서·PDF 보고서·완료 보고 규칙 28개 파일을 `1312252e200df81e352a34570a8561ef049fb84c` (`feat: implement real Minecraft reset and verified pause (#3)`)로 커밋하고 `git push -u origin ticket-3`가 성공했다. 원격 신규 브랜치 생성과 upstream 설정, 로컬/추적 브랜치의 일치를 확인했다. 게임 jar·월드·raw artifact·캐시·비밀값은 포함하지 않았다.

커밋 직전 pytest 27개·strict mypy 12개 파일·Node 구문·공백 검사와 기존 실제 시계 검증 fingerprint 일치 확인을 통과했다. 실제 게임 63회는 재실행하지 않았다. 기존 PDF의 작성 당시 미커밋 상태를 보존하고 보고서 목록에 후속 코드 커밋/푸시 기록을 연결한다. 이 후속 문서 기록도 별도 커밋으로 같은 브랜치에 푸시한다. main 머지·PR 생성·이슈 종료·브랜치 삭제는 수행하지 않았다.

## 2026-11-03 — ticket-3 커밋·푸시 준비 검사

사용자가 `ticket-3` 변경의 커밋·푸시를 명시적으로 요청했다. main 머지·PR 생성·이슈 종료는 이번 요청에 포함하지 않는다. 원격을 fetch한 결과 기존 origin/ticket-3는 없다. 커밋 직전 전체 pytest **27 passed(8.24초)**, strict mypy **12개 파일 통과**, Node backend/lifecycle 구문 검사와 diff 공백 검사 통과를 확인했다. 현재 시계 엔진·설치 환경 fingerprint가 보존된 실제 63/63 검증 기록과 일치하고, 보고서 PDF 2쪽/3쪽의 한글 추출도 재확인했다. 실제 63회 게임 검사는 재실행하지 않았다.

코드·설정·문서·보고서만 커밋하며 게임 jar·월드·원시 실행 산출물·캐시·비밀값은 제외한다. 기존 PDF의 Git 상태는 작성 당시 기록으로 보존한다. 커밋·푸시 결과는 원격 확인 후 이어서 기록한다.

## 2026-11-03 — 이슈별 검토 PDF와 완료 절차 추가

사용자가 이슈 완료마다 별도 폴더에 검토 PDF를 저장하도록 요청했다. `reports/`를 만들고 #2/T01 회고 보고서 2쪽, #3/T02 구현·검증 보고서 3쪽 및 편집 가능한 HTML 원본·공통 CSS·템플릿·목록/출력 규칙을 저장했다. 작성일은 2026-11-03, 검증 기준일은 2026-11-02로 구분한다. #2의 당시 검사 기록과 main 반영, #3의 현재 미커밋·미푸시·미머지/이슈 종료 미처리 상태를 명시했다.

`AGENTS.md`에 이슈 완료 보고 전 PDF·HTML 저장과 가독성 검사 규칙을 연결했고, root README에 보고서 목록 링크를 추가했다. 기존 완료 보고서를 보존하고 후속본은 날짜/버전으로 구분한다. 사용자 검토 승인을 새로 요구하는 절차나 백그라운드 자동화는 만들지 않았다.

직접 Pango/Cairo를 연결하는 첫 출력 시도는 GI cairo Context 연결 모듈 부재로 실패했다. WeasyPrint 70.0을 Git 제외 `.cache/uv`의 별도 도구 환경에 설치해 출력했다. pyproject.toml/uv.lock/Node lock은 변경하지 않았다. Noto CJK KR 글꼴은 fontTools fallback으로 subset되며 HarfBuzz-Subset 권고 경고가 있었으나 실제 출력·포함·텍스트 추출을 확인했다.

PDF 검사: A4, #2 2쪽/#3 3쪽, 각 페이지에 충분한 본문, 모든 사용 글꼴 embedded/subset/Unicode mapping 확인. pdftotext로 한글·핵심 수치·미커밋 상태를 대조하고 5개 페이지를 PNG로 렌더링해 직접 확인했다. 초안의 짧은 문장/표 행 단독 페이지는 간격·구성 조정으로 제거했다. PDF/HTML은 모두 reports/에 저장하며 Git 제외 대상이 아니다.

이번 작업은 보고서와 작업 지침 추가다. Minecraft·모델/API·학습·pytest/mypy를 새로 실행하지 않았으며 문서의 실험/검사 수치는 보존된 원시 결과와 PROGRESS/검토 문서를 재구성한 것이다. 커밋·푸시·머지·이슈 종료는 수행하지 않았다.

## 2026-11-02 — 이슈 #3 실제 서버·snapshot·정지 구현 및 검증

사용자가 Minecraft EULA에 명시적으로 동의하고 서버 실행을 승인했다. 보유 계정이 필요한지 추가로 물었으며 서버 프로세스와 loopback offline 봇 접속에는 계정 인증을 사용하지 않는다고 설명했다. 계정·비밀번호·토큰·유료 서비스는 사용하지 않았다. 브랜치는 `ticket-3`, 기준은 main `1de47b7`이다.

### 실제 설치와 구현

- Java 21.0.12.1, Node 24.20.0, Mineflayer 4.39.0, Minecraft 1.16.5, Fabric Loader 0.16.14, launcher/installer 1.1.1, Carpet 1.4.44+v210714를 연결했다. 게임 바이너리·16개 jar의 SHA-256·승인일·버전은 Git 제외 경로 `worlds/server/installation.json`에 보존했고 출처·라이선스·주요 hash는 third_party/README.md에 기록했다. Mojang server.jar와 Fabric이 실제 받은 jar 모두 공식 SHA-1 `1b557e7b033b583cd9f66746b7a9ab1ec1673ced`와 일치한다.
- 서버는 `127.0.0.1:25565`, Survival/Peaceful, offline 인증, RCON 비활성이다. 실제 Done과 ResearchBot 접속·체력 20·위치를 확인했다. Microsoft/yggdrasil 인증 경로와 기존 npm audit 경고를 해결·검증했다고 표시하지 않는다.
- 최초 수동 서버는 로그상 15:09:03에 준비됐고 21:30에 저장·종료했다. 이 대기 중 실행을 학습/평가 경험으로 세지 않는다. 이후 진단은 CLI가 서버를 시작·정리한다. GPU 모델·API 지출은 없으며 PC 180시간의 충분성은 미확인이다.
- 기존 Python 실행기·자료형·JSONL을 유지하고 Node backend를 연결했다. 관리자 FD는 reset·snapshot 준비·시계 진단/검증만, 정책 stdin은 observe/step만 허용한다. 시드·숨은 블록·관리자 정보·자유 콘솔 실행을 정책에 제공하지 않는다. 현재 실제 관측은 자기 상태, 지형 지도는 빈 목록이며 실행은 wait다. 미지원 유효 행동의 실패도 실제 1틱을 실행해 invalid로 기록한다. 지형 관측·다른 매크로는 후속 티켓이다.
- `prepare-world`, `configs/minecraft.yaml`, `verify-clock`을 추가했다. 시드 `20261102`는 최초 생성 전에 기록했다. C4/G1은 첫 자연 지상 spawn `[-240.5,65,186.5]`·빈 인벤토리, G2/G3는 같은 위치에 돌/철 곡괭이 각 1개다. G4는 동일 x/z의 y=11에서 철 곡괭이를 제공하며 y=10의 3×3 바닥·y=11–13의 3×3 공간을 관리자 준비했다. 광석이나 모델 성적을 조회해 고르지 않았고 자연 C4 도달/다이아 성공으로 세지 않는다.
- 과제별 snapshot.json에 전체 월드 hash·좌표·제공 상태·준비 출처를 보존했다. C4/G1 `f8c9dfe69babead6d1d32fd5f4d3e54a22e5815b29d3c59fff7a0d6c3b3448c2`, G2 `0372a21c3501f5ad9a437522a75fe7bdb1a932a9c279d18e31e762a57c7bb969`, G3 `a189a17386976c74b3d4db82467a6bd62e42bf35fd384f78a3eacdd7dea551bb`, G4 `e56ebc58e4536e319af3e0440eafdb25d44973ce8780a301479eb4c20592ee0b`다.
- reset은 원본 hash 확인→staging 복사/재검증→디렉터리 교체→서버/새 bot 재시작을 따른다. 새 관측 UUID·episode/attempt·입력·이력·시간·사건 상태로 이전 에피소드를 섞지 않는다. 원본 덮어쓰기·심볼릭 링크를 거부한다. 서버 디렉터리는 `flock` 커널 잠금으로 소유하고 종료/충돌 시 해제한다.

### 실제 정지 실패와 보완

- Carpet freeze와 `physicsEnabled=false`만 쓴 실제 침수 5초 시험은 게임 틱이 같은데도 Air 281→172로 실패했다. 원시 기록은 `artifacts/issue-3/carpet-water-before-repair.json`이다.
- 자체 `bridge/pausemod/`는 Carpet이 paused이며 활성 틱이 아닌 동안 player tick/playerTick과 이동·차량 이동을 중지한다. 네트워크/keepalive는 유지하며 시작부터 월드를 정지한다. 초기 로그인용 체력·인벤토리·metadata는 실제 저장 상태에서 따로 전송한다. 모드 jar SHA-256은 `169c35019242042f8e93c32a72d9b5d866d130f589234eae89d44d39e3bd5cbb`다.
- 개발 중 Mixin namespace의 initializer 로딩 오류, 초기 체력 패킷 부재로 인한 spawn timeout, 2초 종료 유예로 인한 소유권 파일 잔류를 실제 로그로 확인했다. namespace·초기 상태 전송·제한된 spawn 대기·15초 종료 유예·진행 작업 중단·커널 잠금으로 보완했다.
- 보완 후 침수 5초와 7장면의 짧은 실제 시험은 준비 상태/불변을 확인했다. 첫 전체 실행은 상태 변화가 없었지만 화염 한 건이 아직 발화하지 않아 **62/63**, pause_verified=false로 실패했다. `verify-clock-attempt-1.jsonl`에 보존했다. 화염 준비를 실제 25틱 접촉으로 수정했다.
- 최종 공개 `verify-clock --config configs/minecraft.yaml`: **7장면×0/5/10초×3회, 63/63 통과, exit 0**. 전후 전체 측정값은 같고 위치 drift는 모두 0이다. 낙하 장면은 모두 공중 상태임도 원시 기록에서 확인했다. 전체 경과 **459.35초**, user 109.96초, sys 3.14초. 원시 JSONL·실패 시도·경과시간은 `artifacts/issue-3/`에 보존했다.
- 성공 실행만 검증 기록을 원자 저장한다. 코드·게임 jar·의존성 lock·Java/Node·서버 설정·과제 snapshot manifest의 fingerprint가 일치할 때만 후속 step의 pause_verified를 인정한다. 현재 `37929b6539994f39799f7e1e220637077e26bb0fa8b42bfa6c7f6326136942a9`이며 최종 실험 lock은 T19에서 수행한다.

### 개발 검증과 최종 확인

최종 전체 pytest **27 passed(8.14초)**, strict mypy **12개 파일 통과**(로컬 실제 reset 검사 스크립트 포함), diff 공백 검사 통과. 관리자 권한 거부, 상태 변화·미준비/잘못된 시계 응답 거부, 손상/symlink snapshot에서 현재 월드 보존, 느린 backend 종료 정리의 공개 CLI 회귀 검사를 포함한다. mock/scripted RPC 검사를 실제 물리 근거와 구분한다. 마지막 CLI 오류 처리도 RED→GREEN으로 확인해 실제 clock 오류를 mock smoke summary로 표시하지 않고 unverified clock_summary로 끝낸다. 이 오류 응답 보완은 검증한 시계 엔진/게임 모듈을 바꾸지 않는다.

읽기 전용 검토의 중요 지적 6건(관측 ID의 reset 간 재사용, 종료 유예, 연결 종료 후 cached 관측, snapshot 루트 symlink, 드롭 timestamp 비교, 마지막 틱 실패의 invalid/truncated 중복)을 확인·수정했다. symlink와 종료 정리는 RED→GREEN으로 확인했다. 상세는 docs/reviews/issue-3.md다. 별도 재검토, 커밋·푸시·머지·이슈 종료는 수행하지 않았다.

최종 실제 확인:

- 공개 smoke exit 0, 2결정·실측 40틱·11.18초, 두 step의 pause_verified=true, actor 전이 0·진단 보상 0·다이아 성공 false·decision_limit 유효 절단이다. 원시 결과는 `artifacts/issue-3/smoke-episode.jsonl`이다.
- C4에서 3틱 wait 후 다시 reset해 위치·속도·체력·산소·인벤토리·활성 시간 0의 복원을 확인했다. reset 전 후보는 invalid_selection으로 거부됐고 활성 시간은 여전히 0이었다. 미지원 행동은 실제 1틱을 실행해 invalid=true/truncated=false로 반환했다. 해당 Java 서버에 SIGTERM을 보내 연결을 종료한 뒤 cached 관측을 반환하지 않고 backend_error로 거부함을 확인했다.
- G1–G4도 각각 실제 재기동/reset 후 고정 좌표·제공 도구·체력 20·활성 틱 0, reset/observe 일치를 확인했다. 마지막에 flock을 다시 획득할 수 있어 소유권이 남지 않았음을 확인했다. 검사 코드/결과는 `artifacts/issue-3/reset-check.py`와 reset-check.json이다.
- 최종 C4 복원 후 실제 level.dat의 Time=457156, DayTime=1001, 비/천둥 여부와 타이머가 원본 snapshot과 같음을 NBT로 확인했다. `artifacts/issue-3/reset-world-clock.json`에 기록했다.
- 사용자 요청대로 C4 기준으로 수동 서버를 다시 실행했다. 23:22:20 Done, `127.0.0.1:25565`, 자체 확장의 정지 상태이며 23:24:57 list에서 접속자 0/1을 확인했다. 수동 실행도 동일 flock을 소유하므로 다음 실험 CLI 전 콘솔 stop으로 종료한다. 현재 실제 서버가 실행 중이라는 사실과 이슈 #3의 검증 완료를 구분한다.

모델/학습/PPO·전체 C4/G4 평가·온라인 계정 인증·공개 서버는 미실행이다. doctor의 기존 환경 probe를 새 게임 검증으로 바꾸지 않았으며 전체 실험 준비 완료를 주장하지 않는다. 향후 게임/버전/실행기 수정 시 시계를 다시 검증하고 T19에서 예산과 최종 lock을 고정한다.

## 2026-11-02 — 이슈 #3 / ticket-3 착수

사용자 요청으로 main `1de47b7`에서 `ticket-3` 브랜치를 생성·전환했다. 최초 생성은 샌드박스의 `.git/refs` 쓰기 제한으로 실패했으며 권한을 허용한 재실행은 성공했다. 기존 파일·Git 이력을 보존했으며 commit/push/merge는 수행하지 않았다.

- GitHub #1/#3 본문·댓글을 재조회했다. 둘 다 댓글이 없으며 #1 본문은 로컬 PRD와 일치한다. 선행 #2는 완료됐다. PLAN §§4.1–4.3, 12–14와 기존 schema/RPC/episode/CLI·Mineflayer 물리 코드를 확인했다.
- 구현 범위는 실제 Minecraft 1.16.5 Survival/Peaceful 연결, 사전 선정한 단일 시드와 C4/G1–G4 기준 snapshot/hash, 완전 reset, 실제 wait/실패 틱 계측, 관리자·정책 권한 분리를 유지하는 결정 경계 정지 및 공개 `verify-clock`이다. 평지·제련·드롭·용암·낙하·침수·화염의 0/5/10초 지연 각 3회, 위치 오차 0.001블록과 상태·사건·틱 불변을 실제 검증해야 한다.
- 현재 Python RPC의 별도 관리자 FD와 정책 stdin을 재사용할 수 있다. Mineflayer의 `physicsEnabled=false`만으로 서버 정지를 증명할 수 없다. Fabric/Carpet 연결을 제안했으며 서버·플레이어의 실제 정지 여부에 따라 보완해야 한다. 공식 Carpet 1.4.44 release에 `fabric-carpet-1.16.5-1.4.44+v210714.jar`가 있음을 확인했지만 설치·revision/hash 고정이나 호환 검증은 아직 수행하지 않았다.
- 저장소 파일 조사에서 Minecraft 서버 jar·server.properties·eula.txt를 찾지 못했다. AGENTS.md의 라이선스 동의 규칙에 따라 사용자에게 [Minecraft EULA](https://www.minecraft.net/en-us/eula) 동의와 로컬 서버 다운로드·실행 승인을 요청했으며 답변 대기 중이다. 구현 방식의 위임 또는 설계 선검토 선호도 함께 요청했다. EULA를 대신 수락하거나 서버를 다운로드·실행하지 않았다.

기준 검증: `UV_CACHE_DIR=.cache/uv .tools/uv run --locked --no-sync pytest` 17 passed(3.39초), 같은 환경의 `mypy .` 9개 파일 통과. 현재 Java 21.0.12.1과 Node 24.20.0을 확인했다. 실제 Minecraft 호환·reset·정지·위험 장면 검증은 미실행이며 이슈 #3을 완료로 표시하지 않는다. 다음 작업은 승인 답변을 반영해 서버 구성·출처/버전 고정과 구현 설계를 확정하고 기존 공개 CLI 테스트를 확장하는 것이다.

## 2026-10-10 — S 필수 진단·연구 동기와 기존 이슈 동기화

기준 원격 main은 `d809cd9bbbe2deda0ed193a9120c4964911a9185`다. PR #26은 2026-10-10 06:09:35 UTC에 main으로 머지됐고 T01(#2)은 Closed, T02(#3)는 Open이다. 나머지 구현 티켓 T03–T24도 Open이다. Issue #1과 24개 구현 티켓의 본문·댓글(모두 없음)·상태·라벨·blocking 관계 및 원격 main의 기준 문서를 읽었다. 로컬 main은 처음부터 같은 commit이며 미커밋 변경/분기 커밋이 없었다. `git merge --ff-only origin/main`은 샌드박스의 `.git/ORIG_HEAD` 쓰기 제한으로 실패했으나 이미 원격과 일치해 최신화할 commit은 없었다. 기존 파일/이력/T01 코드는 보존했다.

- PLAN v1.9-core-F-S, PRD v1.2-core-F-S, DECISIONS v1.3-core-F-S와 AGENTS/README/GLOSSARY를 갱신했다. 기존 선택 S=규칙 계획/규칙 행동 정의를 동일 최종 7B+별도 규칙 선택기로 바로잡았다. 규칙 복구/매크로 실행과 구분하고 공통 Observation/Goal/최대 8개 Candidate/mask·candidate_id 계약·일반 규칙·정보 경계·동률/실패 처리/hash 고정을 명시했다.
- 핵심 A/B/J/F C4 22+G4 6=28회/축소 14+6=20회는 보존하고 별도 필수 S C4 결정적 1회를 더해 총 29/21회로 정했다. 최대 활성 13/9시간, 최초 시도 게임 경과 상한 39/27시간이며 reset/검증/서버 재시도는 별도다. S1의 성공/최고 단계·시간·선택/7B 계획 호출·실패·비용은 별도 분모/표이며 단 한 번으로 통계적 우월성·일반적 신경망 대체를 주장하지 않는다.
- S 선택 연산·7B 계획 호출·GPU/PC·실행 비용과 계획 여유를 사전 예산/lock에 포함한다. 180시간의 충분성은 미확인이며 임의 증액/핵심군 삭제를 허용하지 않는다. F 핵심 지위·조건부 7B 학습의 최후 제안/여섯 조건/별도 승인·30,000결정·보상/PPO/curriculum/checkpoint/G4·BC 제외·고정 월드/시작 상태·Jev US$5/Astra 별도 승인 조건을 유지했다.
- 외부 상위 계획과 로봇 내부 소형 행동 선택의 계층 구조를 응용 동기로 추가했다. 현재 7B는 로컬이고 NanoJev는 고수준 매크로 선택 정책이다. 실제 로봇/온디바이스/분산 구조·CPU 실시간/특정 하드웨어 성능은 미검증이며 관련 실험은 추가하지 않는다.
- GitHub #1, #9(T08), #13(T12), #20(T19), #23(T22), #25(T24)만 갱신했다. T08 구현, T12 슬롯 기반/후속 S 연결, T19 사전 비용/규칙/lock, T22 최종 S1, T24 별도 보고로 배치했으며 기존 blocking 그래프를 그대로 활용한다. 새 티켓/테스트 계층은 만들지 않는다.

검증: 전체 pytest 17개 통과(3.38초), strict mypy 9개 파일 통과, diff 공백 검사 통과. 일회성 문서 검사로 PLAN §§6.1–6.2/8/9.4 및 PRD §§4–6 원문 보존, 과거 DECISIONS 이력 보존, 기준 파일 SHA-256, 기본/축소 횟수·활성/경과 상한·180시간 산술을 확인했다. src/tests/configs/fixtures/bridge/의 변경은 없다.

GitHub 게시 직전 전체 25개 이슈가 초기 조회와 같음을 확인했다. 검증된 로컬 문서/hash → #1 → 영향받는 미완료 티켓 5개의 순서로 게시하고 전체를 재조회했다. #1 본문은 로컬 PRD와 정확히 일치하며 여섯 변경안의 본문/제목도 일치한다. 미수정 이슈 19개(Closed #2 포함) 원문과 모든 상태·라벨·댓글·blocking 링크를 보존했다. #1만 새 버전에 맞춰 제목을 바꾸고 다른 제목은 유지했다. 새 이슈·댓글·라벨·상태 변경은 없다. 원격 main은 PR 검토 전 이전 버전이므로 Issue #1의 명세 버전/hash를 기준으로 구분한다.

이번 작업은 문서·이슈 명세 보완이다. 실제 S/Minecraft/T02 이후 구현·학습·유료 모델 API·결제·CPU/네트워크/로봇 실험은 수행하지 않았다. 현재 모의 고정 선택/collect 실행을 S 구현으로 표시하지 않는다. 후속 검증에서 S 구현/실제 수행·규칙 고정·예산 충분성을 확인해야 한다. 사용자 마지막 요청에 따라 로컬 main에 이 변경을 커밋하고 같은 commit의 별도 PR 브랜치를 준비한다. 원격 main 반영/최종 PR 머지와 기존 브랜치 삭제는 수행하지 않는다.

## 2026-10-10 — 티켓 #2 최종 검토 및 통합 준비

사용자가 #2 완료 확인 후 push·merge를 요청했다. 최신 GitHub #1/#2 본문·댓글(둘 다 댓글 없음), 원격 main `3183b52`, ticket-2 `5c26f95`를 대조했다. 독립 Standards/Spec 검토 모두 중대한 지적 0건이며 #2 수락 기준에서 빠진 구현이나 추가 코드 수정은 없다. 별도 승인된 연구 계획/설치 규칙 문서를 함께 통합한다.

- 전체 pytest 17개 통과(3.51초), strict mypy 9개 파일 통과, diff 공백 검사 통과.
- 공개 smoke CLI의 reset→관측→목표→후보→선택→실행→보상→요약 JSONL을 재확인했다. 모의 목표 완료·1결정·20틱·진단 보상 1.0·확률 null·actor 전이 0·다이아 성공 false다.
- 샌드박스 doctor는 GPU 드라이버 접근 오류(exit 9)를 기록했고, 장비 접근을 허용한 재실행에서 RTX 5070 Ti/driver 595.91.07/16303 MiB 및 실제 GPU 합계 10을 확인했다. Python/Node/Java도 합계 10, Mineflayer 4.39.0 import를 확인했다.
- nvcc 부재는 유지되므로 실제 doctor는 cuda=missing·ready=false·exit 1이다. 진단 기능 검증과 전체 실험 환경 준비를 구분한다. 실제 Minecraft/모델/API/PPO는 후속 티켓이며 미검증 상태다. 기존 인증 의존성 npm audit 경고는 이번에 재검사하거나 해결된 것으로 표시하지 않는다.

검토 상세: `docs/reviews/issue-2.md`. 유료 호출·학습·결제는 수행하지 않는다. 기존 티켓·문서 변경을 포함한 검증된 브랜치를 push하고 main에 통합한 뒤 원격 결과를 확인한다.

## 2026-10-10 — 새 PRD와 기존 구현 티켓 일치화

사용자의 추가 요청으로 기존 구현 이슈 #9, #10, #12, #16, #17, #18, #20, #21, #22, #23, #25의 본문·수락 기준을 GitHub에 갱신했다. #10/#17/#23의 제목을 새 범위에 맞추고 참조 제목도 맞췄다. #18은 #10 의존 링크의 표시 제목만 변경했다. PRD/#1의 기존 '다른 티켓은 변경하지 않는다' 문구도 이번 추가 요청에 맞춰 동기화했다.

- #9/#10: 공통 목표·검증·재계획·복구와 계획기 모델/출처, 고정 7B와 Astra backend·실제 접근/지원 설정/예산 진단. #12: J/F 동일 Jev와 진단·실패/재시도 포함 합산 US$5, 별도 Astra ledger/승인 상한.
- #16/#17: 초기 계획 오류/원인 진단, 지식·입력·검증·재계획 보완, 공통 계획 상태 6건 비교, 여섯 조건의 마지막 학습 제안·명시적 승인 절차. 실제 계획기 학습은 티켓 완료 기준이나 자동 분기가 아니다.
- #20/#21/#22: F 접근·비용·시간/GPU/PC의 본 학습 전 확인, 조건부 학습을 선택한 경우만 승인·PPO 전 완료/재검증, A/B/J 동일 최종 7B 고정. 행동 학습량·알고리즘·checkpoint 선택 규칙은 유지하며 F/계획기 진단 결과로 B checkpoint를 고르지 않는다.
- #23/#25: 핵심 A/B/J/F C4 기본 22회/공통 축소 14회와 필수 G4 6회(총 28/20회), F 미실행 예정 슬롯·질문 미검증, 네 비교의 해석과 비용/실패 보고. B↔F는 전체 시스템 비교다.

검증: 게시 직전 전체 25개 이슈가 초기 조회와 같음을 확인했다. 게시 후 전체를 다시 조회해 수정안 본문·제목 및 PRD 기준 파일 SHA-256의 일치, 미수정 티켓의 원문 보존, 전체 라벨·상태·댓글·의존 ID 및 참조 제목 보존/일치를 확인했다. 새 이슈·댓글·라벨·상태 변경은 없다. `git diff --check` 통과.

현재 추가 티켓은 필요 없다. Astra 연결은 #10, 공통 계획 비교·조건부 학습 검토/제안은 #17에서 담당한다. 향후 실제 계획기 학습을 별도 승인할 경우에만 구체적인 학습 실행 티켓의 필요성을 다시 보고한다. 작업 브랜치는 `ticket-2`이며 이번 변경은 문서/티켓뿐이다. 코드·학습·유료 모델 API·결제·Git commit/push/merge는 실행하지 않았다. Astra/Jev 실제 접근·과금·지연과 180시간 내 수행 가능성은 후속 승인된 진단에서 확인해야 한다.

## 2026-10-10 — 핵심 F 복원 및 조건부 계획기 학습 문서 수정

기준: PLAN v1.7-prd-final, DECISIONS의 기존 결정, GitHub #1 본문·댓글(댓글 없음), 관련 기존 티켓. 작업 브랜치는 `ticket-2`; 기존 #2 구현 commit `19e64cb`와 별도의 미커밋 문서 변경이다. commit/push/merge는 수행하지 않는다.

- PLAN v1.8-core-F, DECISIONS v1.2-core-F, PRD v1.1-core-F와 README/AGENTS/GLOSSARY의 상충 규정을 갱신했다. 과거 결정 본문은 보존하고 현행 결정의 대체 범위를 명시한다.
- F=Astra+J와 동일 Jev를 핵심 비교로 복원한다. 기본 기존 C4 17+F 5+G4 6=28회, 공통 축소 C4 14+G4 6=20회다. 행동 PPO 30,000결정·보상/SMDP/PPO·checkpoint/실패/복구 규칙은 유지한다.
- 계획기 학습은 진단→지식·입력·검증·재계획 보완→공통 Astra 6상태 비교→여섯 조건 검토→별도 제안·분석/비용 보고→명시적 승인 순서의 마지막 대안이다. 실제 학습은 수행하지 않으며 승인한 경우만 PPO 전에 마치고 A/B/J 최종 7B를 동일하게 고정한다.
- 2026-10-10 공개 페이지에서 Jev US$0.042/0, Astra 표준 US$10/50(입력/출력 100만 토큰당)을 조회했다. 실제 접근·응답·사용량·과금·지연은 미검증이다. PLAN §11.1.1의 추가 비용 US$4.17 및 20% 여유 US$5.004는 명시된 토큰/요청 가정의 예시이며 지출 승인이 아니다. Jev 총 US$5는 J/F·진단·실패/재시도 합산, Astra 별도 상한은 미승인이다.
- F 5회 추가 활성 상한 2.5시간, 최초 시도 게임 경과 상한 7.5시간이며 reset/진단/재시도는 별도다. 기본 전체 최초 시도 상한 37.5시간은 기존 최종 평가 배정 27시간을 넘는다. 실측 평균에 따른 재산정 없이 기존 PC 180시간의 충분성을 주장하거나 증액하지 않는다. GPU 연산/PC 점유는 따로 측정해야 한다.
- 구현 영향: 현재 CLI는 doctor/smoke-episode, Goal은 fixed collect, EpisodeSummary는 smoke 전용이고 실제 계획기·A/B/J/F selector·예산/학습/evaluate는 아직 없다. src/tests/configs/fixtures/의 이번 코드 변경은 필요하지 않다. 후속 구현에서 Astra backend·공통 계획기 출처/model ID·J/F 합산 비용·평가 슬롯/lock을 반영해야 한다.

PRD 갱신 단계에서는 기존 티켓을 수정·생성하지 않고 다음 변경 필요성을 보고했다. 이후 사용자의 추가 요청으로 위 기록과 같이 기존 티켓을 갱신했다.

|기존 이슈|변경 필요성|
|---|---|
|#9 / T08|공통 목표·복구 로그에 7B/Astra 모델과 출처를 함께 기록|
|#10 / T09|기본 7B 고정은 유지하고 공통 Astra backend·접근/설정 진단 범위를 반영|
|#12 / T11|J/F 전체 Jev US$5 집계·F 예정 비용 예약·미실행 질문 범위|
|#16 / T15|기존 A/J 진단의 계획 순서/반복/관측 불일치·원인 분류와 공통 6상태 계획 비교|
|#17 / T16|지식 조회 뒤 입력/검증/재계획 보완·Astra 비교·여섯 조건의 마지막 별도 제안. 학습 실행을 필수 수락 기준으로 만들지 않음|
|#20 / T19|F 우선 접근/별도 Astra 예산·시간/GPU/PC·Jev 합산·28/20슬롯·조건부 최종 7B/hash/승인을 lock에 반영|
|#21 / T20|본 PPO 전 조건부 계획기 준비 종료·최종 고정 확인; 학습량/알고리즘은 유지|
|#23 / T22|제목·본문 A/B/J/F, C4 22/14회·F 미실행/Q3/Q4 미검증|
|#25 / T24|J↔F/B↔F와 전체 시스템 해석, 계획기 전후 별도 진단·F 비용/미검증 보고|

GitHub #1 제목·본문을 v1.1-core-F로 갱신하고 재조회해 로컬 PRD와의 일치 및 라벨·댓글 보존을 확인했다. 게시 전 최신 본문과 초기 조회본이 일치하는지도 확인했다.

검증: `git diff --check` 통과. 일회성 문서 검사를 통해 PLAN §6.1–6.2(Choice/PPO), §8(보상/커리큘럼/학습량), §9.2(checkpoint/복구), §9.4(G4)와 PRD §4/§6의 원문 일치, 과거 DECISIONS 본문 보존, 기준 파일 SHA-256, 평가 수/시간 상한/API 가정 산술을 확인했다. 변경 파일은 문서 7개뿐이다. 코드 변경이 없어 pytest/mypy·실제 게임/모델/API 검사는 이번에 재실행하지 않았다. 학습·유료 모델 API·결제·새 티켓·Git commit/push/merge는 이번 작업의 실행 범위에 없다.

## 2026-10-09 — 이슈 #2 / ticket-2

기준: GitHub #1 본문·댓글(댓글 없음), #2 수락 기준·댓글(댓글 없음), PLAN.md §§12–14. 시작 commit `3183b52270b8025144b56d955768ca27332e225e`; 기존 작업 변경 없음.

### 구현

- Python/uv 패키지와 공개 `doctor`, `smoke-episode`, pytest/mypy 설정 및 의존성 lock.
- Observation/Goal/Candidate/SelectionResult/StepResult/EpisodeSummary, episode/attempt/candidate/source-observation ID, 저장 후보·mask, JSONL 출력과 구조화 오류.
- 관리자 FD와 정책 stdin을 구분하는 subprocess RPC. 모의 fixture backend와 같은 실행기를 사용하는 대체 RPC 설정.
- 고정 원목 목표의 reset→관측→후보→선택→step→획득 사건 진단 보상→summary. terminal/유효 절단/무효/backend 오류 구분; 미제공 확률 null; actor 경험 0; 다이아 성공 false.

### 실제 환경 진단

|검사|실제 결과|
|---|---|
|Python|3.12.3; sum(0..4)=10|
|uv|0.12.23; `.tools/uv`에 설치, PATH 영구 변경 없음|
|Node/npm|24.20.0 / 11.19.0; Node sum(0..4)=10|
|Java|OpenJDK 21.0.12.1; 임시 Java 소스 실행 sum(0..4)=10|
|GPU|접근 허용 실행에서 NVIDIA RTX 5070 Ti, driver 595.91.07, 16303 MiB|
|GPU 연산|자체 PTX 커널로 sum(0..4)=10, CPU로 복사한 결과 일치|
|CUDA toolkit|nvcc 없음; doctor의 cuda=missing, ready=false, exit 1|
|Mineflayer|4.39.0 설치/import 및 createBot export 확인. 서버 연결 없음|
|개발 검사|pytest 9.1.1, mypy 1.20.2 설치|

제한된 샌드박스에서는 nvidia-smi가 driver 통신 실패(exit 9)였지만 권한 있는 실제 장비 조회와 GPU 연산은 통과했다. Java 21과 Minecraft 1.16.5의 실제 호환·게임 정지는 검증하지 않았다.
시스템 Python의 pip/ensurepip는 없었으며 uv로 가상환경을 만들었다. 첫 pytest 실행은 시스템 ROS plugin이 lark를 요구해 실패했고 plugin 자동 로드 해제로 해결했다.

### 검증 기록

- 첫 CLI 성공 테스트: 구현 전 exit 1로 RED, 구현 후 PASS.
- doctor 테스트: 명령 미구현으로 RED, 실제/부재/실행 오류 보고 구현 후 PASS.
- backend 실행 불가 요약·정책 채널 EOF 종료·다중 결정 획득 기억: RED 확인 후 수정, 각각 PASS.
- GPU probe: 모듈 부재로 RED, 실제 장비에서 산술 출력 10으로 PASS.
- 마지막 개별 파일 검사: `uv run pytest tests/test_cli.py -q` 16 passed; `uv run mypy .` 통과.
- `npm --prefix bridge ci --ignore-scripts` 설치 통과. npm audit는 uuid 권고에서 전파된 moderate 6건을 보고(exit 1)했으며 무리한 자동 downgrade/override는 적용하지 않았다. 상세 출처는 third_party/README.md 참조.
- 최종 `npm --prefix bridge ci --cache .cache/npm --offline`은 scripts를 포함해 설치 통과했고 이후 Mineflayer 4.39.0 import를 확인했다. offline 설치의 “0 vulnerabilities” 출력은 온라인 보안 권고 검사를 대체하지 않으며 앞서 확인한 6건을 해결한 결과가 아니다.
- 최종 전체 검사: `uv run pytest` 17 passed(3.39초), `uv run mypy .` 9개 파일 통과, `git diff --cached --check` 통과.
- 공개 CLI 수동 실행: 모의 원목 목표 완료, 1결정·20활성 틱·진단 보상 1.0, 실제 다이아 성공 false, actor 전이 0, exit 0.
- Standards 리뷰 0건. Spec 리뷰 P2 2건(잘못된 요청의 유효 ID 상실, 사건 출처 mock 전용)을 재현 테스트 RED→GREEN으로 수정했다. 실제 출처 wire 호환 검사는 외부 scripted RPC이며 게임 검증이 아니다. 상세: docs/reviews/issue-2.md.

### 미실행 및 다음 작업

실제 Minecraft backend/reset/freeze·정보 감사·게임 물리·계획기/NanoJev/Jev·과금·연구 보상/PPO·실험 lock·학습·평가는 미구현/미실행이다. 모델·월드·서버 revision/hash를 임의 고정하지 않았다. API 요청과 비용은 없다.
후속 티켓에서 실제 게임 backend와 자료형을 연결하고 clock/정보 경계를 검증한다. Java 호환성과 인증 의존성의 audit 경고를 실제 연결 전에 해결/평가한다. nvcc 부재를 GPU 계산 불능으로 해석하지 않는다.
