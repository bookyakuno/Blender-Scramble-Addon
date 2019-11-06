さいでんか氏の Scramble Addon です。  
Githubが削除されてしまったため追加しました。問題があれば消します。

# Blender-Scramble-Addon
Blenderのかゆいところに手が届くかもしれない機能が詰まったアドオンです。
> This add-on is packed with Blender useful features.
> English-speaking people should be on the English translation.
![Translation](http://i.imgur.com/U1pO6Jh.jpg)

## インストール (Installation)
まず画面右の「Download ZIP」でZIPファイルをダウンロードし解凍。
中の「Scramble Addon」フォルダをBlenderのaddonsフォルダに置いて下さい。
(Windows7なら： C:\Users\ユーザー名\AppData\Roaming\Blender Foundation\Blender\バージョン\scripts\addons\Scramble Addon)
日本語・英語を問わず、国際フォントの使用には必ずチェックを。
Blenderを起動しユーザー設定のアドオンタブで「Scramble」等で検索、アドオンをオンにして「ユーザー設定の保存」クリック。
左上の「ファイル」メニューに「全体処理」という項目が追加されていればインストール成功です。

> Download the ZIP file first in the "Download ZIP" of right and unzip.
> Place a "Scramble Addon" folder in the addons folder of Blender.
> (If on Windows 7: C:\Users\\(UserName)\AppData\Roaming\Blender Foundation\Blender\\(Version)\scripts\addons\Scramble Addon)
> Regardless of Japanese or English for the use of the international font by all means a check.
> Search Start the Blender add-on tab of the user settings in the "Scramble", etc., select the add-on click "save user settings".
> The installation is successful if it is added to item "whole process" in the "File" menu in the upper-left corner.

## 使い方 (How to use)
このアドオンは基本的に、既存のメニューに項目が追加されるのでそれをクリックして実行します。
例えば「ファイル > 全体処理 > オブジェクト > 全ての「すべての辺を表示」をオン」等です。
追加された項目には必ず![アイコン](http://i.imgur.com/OOVguPd.png)のようなアイコンが表示されています。
色々なところに項目が追加されているので探してみてください。

> This add-on is basically, and then run it by clicking on it because the items to the existing menu is added.
> For example, it is the "File> overall process> object> on all of the" Show all sides, "" and the like.
> The added items are always displayed an icon such as ![アイコン](http://i.imgur.com/OOVguPd.png).
> Please look because items have been added to the various places.

## 機能一覧 (List of functions)
* **「プロパティ」エリア > 「ボーンコンストレイント」タブ**
* **―("Properties" Area > "Bone Constraints" Tab)**
    * **クイック・チャイルド**
    * **―(Quick child)**
        * 素早くチャイルドコンストレイントを追加します
        * ―(Quickly add child constraint)
    * **IKのチェーンの長さを設定**
    * **―(Set length of IK chain)**
        * アクティブなボーンのIKのチェーンの長さを第二選択ボーンへの長さへと設定します
        * ―(Chose second length of active bone IK chain to length to bones and set the)
    * **IKのポールターゲットを設定**
    * **―(Set pole target of IK)**
        * アクティブなボーンのIKのポールターゲットを第二選択ボーンに設定します
        * ―(Chose second Paul target of active bone IK bones sets)
    * **IKのポール角度を設定**
    * **―(Setting IK Paul angles)**
        * 選択ボーンのIKのポール角度を自動で設定します
        * ―(Set auto-choice bone IK Paul angles)

* **「プロパティ」エリア > 「ボーン」タブ**
* **―("Properties" Area > "Bone" Tab)**
    * **ボーン名をクリップボードにコピー**
    * **―(Bone name to Clipboard)**
        * ボーン名をクリップボードにコピーします
        * ―(Bone Name to Clipboard)
    * **ボーン名を左右反転**
    * **―(Mirror Bone Name)**
        * アクティブなボーン名を左右反転します
        * ―(Flip active mirror bone name)
    * **ボーン名に文字列を追加**
    * **―(Add text bone name)**
        * アクティブなボーン名に文字列を追加します
        * ―(Adds string to active bone name)

* **「プロパティ」エリア > 「ボーン」タブ > 「インバースキネマティクス (IK)」パネル**
* **―("Properties" Area > "Bone" Tab > "Inverse Kinematics" Panel)**
    * **このIK設定をコピー**
    * **―(Copy IK Setting)**
        * アクティブなボーンのIK設定を、他の選択ボーンにコピーします
        * ―(Copies of other selected bone IK settings Active)
    * **最小/最大角を反転**
    * **―(Invert Minimum/maximum Angle)**
        * このボーンのIK設定の最小角と最大角を反転させます
        * ―(Reverses minimum and maximum angle of IK setup this bone)
    * **軸設定を他の軸にコピー**
    * **―(Copy axis-setting to other axis)**
        * 1つの軸の設定を、他の軸にコピーします
        * ―(Copy settings other axis from one axis)
    * **IK設定をリセット**
    * **―(Reset IK Settings)**
        * このボーンのIK設定を初期化します
        * ―(Reset this bone IK settings)

* **「プロパティ」エリア > 「ボーン」タブ > 「関係」パネル**
* **―("Properties" Area > "Bone" Tab > "Relations" Panel)**
    * **関係設定をコピー**
    * **―(Copy Relations Settings)**
        * アクティブなボーンの関係設定を、他の選択ボーンにコピーします
        * ―(Copies of other selected bone affinity of active bone)

* **「プロパティ」エリア > 「ボーン」タブ > 「トランスフォーム」パネル**
* **―("Properties" Area > "Bone" Tab > "Transform" Panel)**
    * **ボーンの変形をコピー**
    * **―(Copy Bone Transform)**
        * アクティブなボーンの変形情報を、他の選択ボーンにコピーします
        * ―(Copy selected bones of other active bone deformation information)

* **「プロパティ」エリア > 「ボーン」タブ > 「トランスフォームのロック」パネル**
* **―("Properties" Area > "Bone" Tab > "Transform Locks" Panel)**
    * **トランスフォームのロック設定をコピー**
    * **―(Copy Transform Locks Settings)**
        * アクティブなボーンのトランスフォームのロック設定を、他の選択ボーンにコピーします
        * ―(Copies of other selected bone lock setting active bone transform)

* **「プロパティ」エリア > 「アーマチュアデータ」タブ > 「ボーングループ」パネル**
* **―("Properties" Area > "Armature" Tab > "Bone Groups" Panel)**
    * **このボーングループのボーンのみ表示**
    * **―(Show only bone in this bones group)**
        * アクティブなボーングループのみを表示し、その他のボーンを隠します
        * ―(Group active on bones and bones of other hide)
    * **このボーングループのボーンを表示**
    * **―(Show bone in bone group)**
        * アクティブなボーングループを表示、もしくは隠します
        * ―(Active bone group show or hide)

* **「プロパティ」エリア > 「カーブデータ」タブ > 「ジオメトリ」パネル**
* **―("Properties" Area > "Curve" Tab > "Geometry" Panel)**
    * **ジオメトリ設定をコピー**
    * **―(Copy Geometry Settings)**
        * アクティブなカーブオブジェクトのジオメトリパネルの設定を、他の選択カーブにコピーします
        * ―(Copy selection curve of other settings panel geometry of curve object is active)
    * **テーパーオブジェクトをアクティブに**
    * **―(Activate taper object)**
        * テーパーオブジェクトとして指定されているカーブをアクティブにします
        * ―(curve is specified as tapered object)
    * **ベベルオブジェクトをアクティブに**
    * **―(Activate Bevel Object)**
        * ベベルオブジェクトとして指定されているカーブをアクティブにします
        * ―(curve is specified as beveled objects)
    * **テーパーとして使っているカーブをアクティブに**
    * **―(Used as taper curve to activate)**
        * このカーブをテーパーオブジェクトとして使っているカーブをアクティブにします
        * ―(Activates curve as tapered object using this curve)
    * **ベベルとして使っているカーブをアクティブに**
    * **―(Activate bevel curve object)**
        * このカーブをベベルオブジェクトとして使っているカーブをアクティブにします
        * ―(Activates curve as beveled objects using this curve)

* **「プロパティ」エリア > 「モディファイア」タブ**
* **―("Properties" Area > "Modifiers" Tab)**
    * **全モディファイア適用**
    * **―(Apply All Modifiers)**
        * 選択オブジェクトの全てのモディファイアを適用します
        * ―(Applies to all modifiers of selected object)
    * **全モディファイア削除**
    * **―(Remove All Modifiers)**
        * 選択オブジェクトの全てのモディファイアを削除します
        * ―(Remove all modifiers of selected object)
    * **ビューへのモディファイア適用を切り替え**
    * **―(Switch Modifiers Apply/Unapply to View)**
        * 選択オブジェクトの全てのモディファイアのビューへの適用を切り替えます
        * ―(Shows or hides application to view all modifiers of selected object)
    * **モディファイア使用を同期**
    * **―(Sync Modifiers Use)**
        * 選択オブジェクトのレンダリング時/ビュー時のモディファイア使用を同期します
        * ―(synchronized modifier used when rendering selection / view)
    * **全モディファイアの展開/閉じるを切り替え**
    * **―(Toggle all modifiers expand/close)**
        * アクティブオブジェクトの全モディファイアを展開/閉じるを切り替え(トグル)します
        * ―(Expand / collapse all modifiers of active objects to switch (toggle))
    * **モディファイア適用+統合**
    * **―(Apply modifiers + join)**
        * オブジェクトのモディファイアを全適用してから統合します
        * ―(integration from object's modifiers to apply all)
    * **モディファイア名を自動でリネーム**
    * **―(Auto rename modifier names)**
        * 選択オブジェクトのモディファイア名を参照先などの名前にリネームします
        * ―(Rename selected object modifier name refers to, for example,)
    * **ブーリアンを追加**
    * **―(Add Boolean)**
        * アクティブオブジェクトにその他選択オブジェクトのブーリアンを追加
        * ―(Additional Boolean selected objects to an active object)
    * **ブーリアンを適用**
    * **―(Apply Boolean)**
        * アクティブオブジェクトにその他選択オブジェクトのブーリアンを適用
        * ―(Apply to Boolean objects and other active objects)
    * **レンダリング時の細分化数を設定**
    * **―(Set number of subdivision when rendering)**
        * 選択したオブジェクトのサブサーフモディファイアのレンダリング時の細分化数を設定します
        * ―(Sets number of subdivisions during rendering of selected object subsurfmodifaia)
    * **プレビュー・レンダリングの細分化数を同じに**
    * **―(Sync subsurf level preview or rendering)**
        * 選択したオブジェクトのサブサーフモディファイアのプレビュー時とレンダリング時の細分化数を同じに設定します
        * ―(Set in same subdivision of subsurfmodifaia of selected object when you preview and rendering time)
    * **最適化表示を設定**
    * **―(Set Optimization)**
        * 選択したオブジェクトのサブサーフモディファイアの最適化表示を設定します
        * ―(Sets optimization of subsurfmodifaia of selected object)
    * **選択オブジェクトのサブサーフを削除**
    * **―(Delete Subsurfs selected objects)**
        * 選択したオブジェクトのサブサーフモディファイアを削除します
        * ―(Removes selected object subsurfmodifaia)
    * **選択オブジェクトにサブサーフを追加**
    * **―(Add Subsurfs selected objects)**
        * 選択したオブジェクトにサブサーフモディファイアを追加します
        * ―(Add subsurfmodifaia to selected object)
    * **アーマチュアの「体積を維持」をまとめて設定**
    * **―(Set armature "Preserve Volume")**
        * 選択したオブジェクトのアーマチュアモディファイアの「体積を維持」をまとめてオン/オフします
        * ―(Armtuamodifaia selected objects keep volume together off and on the)
    * **クイックカーブ変形**
    * **―(Quick Curve Transform)**
        * すばやくカーブモディファイアを適用します
        * ―(Quickly apply curve modifier)
    * **クイック配列複製+カーブ変形**
    * **―(Quick Array + Curve Transform)**
        * すばやく配列複製モディファイアとカーブモディファイアを適用します
        * ―(Quickly apply curve modifier with modifiers array replication)

* **「プロパティ」エリア > 「アーマチュアデータ」タブ > 「ポーズライブラリ」パネル**
* **―("Properties" Area > "Armature" Tab > "Pose Library" Panel)**
    * **ポーズライブラリを並び替え**
    * **―(Pose Library Sort)**
        * アクティブなポーズライブラリのポーズを並び替えます
        * ―(Sorts by posing for an active pose library)
    * **ポーズライブラリのポーズを最上部/最下部へ**
    * **―(To top/bottom pose of library)**
        * アクティブなポーズライブラリのポーズを最上部、もしくは最下部へ移動させます
        * ―(Active pose of pose library moves to top/bottom)

* **「プロパティ」エリア > 「カーブデータ」タブ > 「シェイプ」パネル**
* **―("Properties" Area > "Armature" Tab > "Shape" Panel)**
    * **シェイプ設定をコピー**
    * **―(Copy Shape Settings)**
        * アクティブなカーブのシェイプ設定を、他の選択カーブにコピーします
        * ―(Copy selected curve other active curve shape settings)

* **「プロパティ」エリア > 「オブジェクト」タブ > 「トランスフォーム」パネル**
* **―("Properties" Area > "Object" Tab > "Transform" Panel)**
    * **シェイプキー名をオブジェクト名に**
    * **―(Shape key name from object name)**
        * シェイプキーの名前をオブジェクト名と同じにします
        * ―(Same as object name name of shape key)

* **「プロパティ」エリア > 「アーマチュアデータ」タブ > 「スケルトン」パネル**
* **―("Properties" Area > "Armature" Tab > "Skeleton" Panel)**
    * **全ボーンレイヤーを表示**
    * **―(View all bone layer)**
        * 全てのボーンレイヤーをオンにして表示します
        * ―(All bone layer and then displays the)

* **「プロパティ」エリア > 「メッシュデータ」タブ > 「UVマップ」パネル**
* **―("Properties" Area > "Mesh" Tab > "UV Maps" Panel)**
    * **まとめてUVをリネーム**
    * **―(Altogether Rename UV)**
        * 選択オブジェクト内の指定UVをまとめて改名します
        * ―(Renames selected objects within designated UV together)
    * **まとめて指定名のUVを削除**
    * **―(Delete UVs specify name)**
        * 指定した名前と同じ名のUVを、選択オブジェクトから削除します
        * ―(Removes selection from UV same name as specified)
    * **UV名を変更**
    * **―(Rename UV)**
        * アクティブなUVの名前を変更します(テクスチャのUV指定もそれに伴って変更します)
        * ―(Renames active UV (UV texture also changes accordingly))
    * **未使用のUVを削除**
    * **―(Remove Unused UV)**
        * アクティブなオブジェクトのマテリアルで未使用なUVを全削除します(他の部分に使われているUVは消してしまいます)
        * ―(Active object material (UV is used in other parts disappear) delete unused UV coordinates to all)
    * **UVを移動**
    * **―(Move UV)**
        * アクティブなオブジェクトのUVを移動して並び替えます
        * ―(Sorts, by moving active object's UV)

* **「プロパティ」エリア > 「メッシュデータ」タブ > 「頂点色」パネル**
* **―("Properties" Area > "Mesh" Tab > "Vertex Colors" Panel)**
    * **頂点色を移動**
    * **―(Move Vertex Color)**
        * アクティブなオブジェクトの頂点色を移動して並び替えます
        * ―(Move vertex color of active objects, sorts)
    * **頂点色を塗り潰す**
    * **―(Fill Vertex Color)**
        * アクティブなオブジェクトの頂点色を指定色で塗り潰します
        * ―(Vertex color of active object with specified color fills)
    * **頂点カラーを一括追加**
    * **―(Altogether add vertex colors)**
        * 選択中のメッシュオブジェクト全てに色と名前を指定して頂点カラーを追加します
        * ―(Specify color and name all selected mesh object, adds vertex color)

* **「ドープシート」エリア > 「キー」メニュー**
* **―("Dope Sheet" Area > "Key" Menu)**
    * **キーフレームを削除 (確認しない)**
    * **―(Delete KeyFrames (Non-Confirm))**
        * 選択した全てのキーフレームを確認せずに削除します
        * ―(Delete without checking all selected keyframes)
    * **全キーフレームを大掃除**
    * **―(Cleaning up all keyframes)**
        * 全てのアクションの重複したキーフレームを削除します
        * ―(Remove keyframe duplicates for all actions)

* **「UV/画像エディター」エリア > 「画像」メニュー**
* **―("UV/Image Editor" Area > "Image" Menu)**
    * **画像名を使用するファイル名に**
    * **―(Image name from file name)**
        * アクティブな画像の名前を、使用している外部画像のファイル名にします
        * ―(External images are using name of active image file name)
    * **全ての画像名を使用するファイル名に**
    * **―(Change all image names to used file name)**
        * 全ての画像の名前を、使用している外部画像のファイル名にします
        * ―(Names of all images using external image file name)
    * **全ての画像を再読み込み**
    * **―(Reload All Images)**
        * 外部ファイルを参照している画像データを全て読み込み直します
        * ―(Reloads all image data referring to external file)
    * **指定色で上書き**
    * **―(Override Color)**
        * アクティブな画像を指定した色で全て上書きします
        * ―(All over colors you specify active image)
    * **指定色で塗り潰す**
    * **―(Fill With Color)**
        * アクティブな画像を指定した色で全て塗り潰します
        * ―(Fill with color image active all)
    * **透明部分を塗り潰し**
    * **―(Fill Transparent)**
        * アクティブな画像の透明部分を指定色で塗り潰します
        * ―(transparent parts of image are active in specified color fills)
    * **画像の正規化**
    * **―(Normalize Image)**
        * アクティブな画像を正規化します
        * ―(Normalize Active Image)
    * **画像ファイル名を変更**
    * **―(Change name of image file)**
        * アクティブな画像のファイル名を変更します
        * ―(Change file name of active image)
    * **画像をぼかす (重いので注意)**
    * **―(Blur image (Note heavy))**
        * アクティブな画像をぼかします
        * ―(Blur Active Image)
    * **水平反転**
    * **―(Flip Horizontally)**
        * アクティブな画像を水平方向に反転します
        * ―(Reverse this image horizontally)
    * **垂直反転**
    * **―(Flip Vertically)**
        * アクティブな画像を垂直方向に反転します
        * ―(Reverse this image verticaliy)
    * **90°回転**
    * **―(Rotate 90 Degrees)**
        * アクティブな画像を90°回転します
        * ―(Rotate active image 90 degrees)
    * **180°回転**
    * **―(Rotate 180 Degrees)**
        * アクティブな画像を180°回転します
        * ―(Rotate active image 180 degrees)
    * **270°回転**
    * **―(Rotate 270 Degrees)**
        * アクティブな画像を270°回転します
        * ―(Rotate active image 270 degrees)
    * **外部エディターで編集 (拡張)**
    * **―(Edit by external editor (Advance))**
        * ユーザー設定のファイルタブで設定した追加の外部エディターで画像を開きます
        * ―(Open image in an external editor of additional files page of custom)
    * **画像の拡大/縮小**
    * **―(Resize Image)**
        * アクティブな画像をリサイズします
        * ―(Resize Active Image)
    * **画像の複製**
    * **―(Copy Image)**
        * アクティブな画像を複製します
        * ―(Duplicate Active Image)
    * **UVグリッドを新規作成**
    * **―(New UV Grid)**
        * WEBからUVグリッドをダウンロードし、画像として新規作成します
        * ―(UV grid to download from WEB, and create new images)
    * **画像を並べる**
    * **―(Tile Image)**
        * アクティブな画像を小さくして並べます
        * ―(Array and scale-down active image)
    * **画像の高速ぼかし**
    * **―(Blur Image Fast)**
        * アクティブな画像に高速なぼかし処理を行います
        * ―(active image blur fast do)
    * **ノイズ画像を新規作成**
    * **―(Create new noise image)**
        * ノイズ画像を新規画像として追加します
        * ―(Add new noise image)
    * **画像を脱色**
    * **―(Decolorize)**
        * アクティブな画像をモノクロにします
        * ―(This decolor active image)
    * **画像のサイズ変更**
    * **―(Change size of image)**
        * アクティブな画像のサイズを変更します
        * ―(Change size active image)

* **「UV/画像エディター」エリア > 「選択」メニュー**
* **―("UV/Image Editor" Area > "Select" Menu)**
    * **分離している頂点を選択**
    * **―(Select Vertex Isolated)**
        * シームによって分離している頂点を選択します
        * ―(Select vertices are isolated by seam)

* **「UV/画像エディター」エリア > 「UV」メニュー**
* **―("UV/Image Editor" Area > "UV" Menu)**
    * **UVをメッシュに変換**
    * **―(Convert UV to mesh)**
        * アクティブなUVを新規メッシュに変換します
        * ―(Converts new mesh to UV active)
    * **UVを島ごとにリサイズ**
    * **―(Resize UV Islands)**
        * UVを島ごとに中心位置を変えてリサイズします
        * ―(UV island into central position and resize)

* **「UV/画像エディター」エリア > 「ビュー」メニュー**
* **―("UV/Image Editor" Area > "View" Menu)**
    * **カーソルの位置をリセット**
    * **―(Reset Cursor Position)**
        * 2Dカーソルの位置を左下に移動させます
        * ―(Move 2D cursor in the lower left)
    * **パネル表示切り替え(モードA)**
    * **―(Toggle Panel (mode A))**
        * プロパティ/ツールシェルフの「両方表示」/「両方非表示」をトグルします
        * ―(properties/tool shelf "both display" / "both hide" toggle)
    * **パネル表示切り替え(モードB)**
    * **―(Toggle Panel (mode B))**
        * 「パネル両方非表示」→「ツールシェルフのみ表示」→「プロパティのみ表示」→「パネル両方表示」のトグル
        * ―("Panel both hide" => show only tool shelf => show only properties => "Panel both display" for toggle)
    * **パネル表示切り替え(モードC)**
    * **―(Toggle Panel (mode C))**
        * 「パネル両方非表示」→「ツールシェルフのみ表示」→「プロパティのみ表示」... のトグル
        * ―("Panel both hide" => "show only tool shelf => show only properties. toggle)
    * **パネル切り替えのパイメニュー**
    * **―(Switch panel pie menu)**
        * パネル表示切り替えのパイメニューです
        * ―(Toggle panel pie menu)

* **「情報」エリア > 「ファイル」メニュー**
* **―("Info" Area > "File" Menu)**
    * **再起動**
    * **―(Restart)**
        * Blenderを再起動します
        * ―(Restart Blender)
    * **最新の自動保存の読み込み**
    * **―(Load Last AutoSave)**
        * 復元するために自動的に保存したファイルの最新ファイルを開きます
        * ―(Open latest file in order to restore automatically saved file)
    * **確認せずに上書き保存**
    * **―(Save Without Confirm)**
        * 確認メッセージを表示せずに上書き保存します
        * ―(Save changes without displaying confirmation message)
    * **最後に使ったファイルを開く**
    * **―(Open last used file)**
        * 「最近使ったファイル」の一番上のファイルを開きます
        * ―(Opens file at top of "recent files)
    * **データ名をリネーム**
    * **―(Rename Data Names)**
        * 全てのデータを対象にしたリネームが可能です
        * ―(Rename using all of data is available)
    * **全ての「すべての辺を表示」をオン**
    * **―(All on "Draw All Edges")**
        * 全てのオブジェクトの「すべての辺を表示」表示設定をオンにします(オフも可能)
        * ―(Show all sides of all objects (can be off) turn display settings)
    * **全ての最高描画タイプを一括設定**
    * **―(Set all maximum drawing type)**
        * 全てのオブジェクトの「最高描画タイプ」を一括で設定します
        * ―(Best drawing types for all objects in bulk set)
    * **全てのデータ名をオブジェクト名と同じにする**
    * **―(All object name to data name)**
        * 全てのオブジェクトのデータ(メッシュデータなど)の名前を、リンクしているオブジェクト名に置換します
        * ―(Replaces object name that linked all object data (mesh data, etc.) name)
    * **全てのマテリアルの「半透明影の受信」をオン**
    * **―(On all material "Receive Transparent")**
        * 全てのマテリアルの「半透明影を受信するかどうか」についての設定をオン(オフ)にします
        * ―(You to receive semi-transparent shadow? "about whether all material (off) on the)
    * **マテリアルのカラーランプ設定を他にコピー**
    * **―(Copy material color ramp settings)**
        * アクティブなマテリアルのカラーランプ設定を他の全マテリアル(選択オブジェクトのみも可)にコピーします
        * ―(Color ramp settings of active material is all material other (only selected objects are allowed) to copy)
    * **アクティブマテリアルのFreeStyle色を他にコピー**
    * **―(FreeStyle color of an active copy to other)**
        * アクティブなマテリアルのFreeStyleの色設定を他の全マテリアル(選択オブジェクトのみも可)にコピーします
        * ―(FreeStyle material active color for all materials other (only selected objects are allowed) to copy)
    * **全マテリアルのFreeStyle色をディフューズ色に**
    * **―(FreeStyle color of all material diffuse color)**
        * 全マテリアル(選択オブジェクトのみも可)のFreeStyleライン色をそのマテリアルのディフューズ色+ブレンドした色に置換します
        * ―(All material (only selected objects are allowed) for FreeStyle line color of material diffuse color + blend to replace)
    * **全マテリアルのオブジェクトカラーを有効に**
    * **―(Enable object colors all material)**
        * 全マテリアルのオブジェクトカラーの設定をオンもしくはオフにします
        * ―(Sets color of all material objects or off the)
    * **全てのバンプマップの品質を設定**
    * **―(Set all bump of quality)**
        * 全てのテクスチャのバンプマップの品質を一括で設定します
        * ―(Bump-map texture of all quality sets in bulk)
    * **全テクスチャ名を使用する画像ファイル名に**
    * **―(All image file names to texture names)**
        * 全てのテクスチャの名前を、使用している外部画像のファイル名にします
        * ―(names of all textures use external image file name)
    * **UV指定が空欄な場合アクティブUVで埋める**
    * **―(Fill active UV if blanks)**
        * テクスチャのUV指定欄が空欄の場合、リンクしているメッシュオブジェクトのアクティブなUV名で埋めます
        * ―(Under active UV texture UV specified fields is linked to an empty mesh object fills)
    * **物理演算の開始/終了フレームを一括設定**
    * **―(Set start/end frame of physics)**
        * 物理演算などの開始/終了フレームを設定する部分にレンダリング開始/終了フレーム数を割り当てます
        * ―(Assign render start / end frames portions to set start / end frames, such as physics)

* **「情報」エリア > 「ファイル」メニュー > 「外部データ」メニュー**
* **―("Info" Area > "File" Menu > "External Data" Menu)**
    * **全ての画像をtexturesフォルダに保存し直す**
    * **―(Resave textures folder, all images)**
        * 外部ファイルを参照している画像データを全てtexturesフォルダに保存し直します
        * ―(All external files referenced by image data to resave textures folder)
    * **texturesフォルダ内の未使用ファイルを隔離**
    * **―(isolate unused files in textures folder)**
        * このBlendファイルのあるフォルダのtextures内で、使用していないファイルをbackupフォルダに隔離します
        * ―(Files in textures folder with Blend files, do not use isolates them in backup folder)
    * **「最近使ったファイル」をテキストで開く**
    * **―(Open Text "Recent Files")**
        * 「最近使ったファイル」をBlenderのテキストエディタで開きます
        * ―(Open "recent files" in Blender text editor)
    * **「ブックマーク」をテキストで開く**
    * **―(Open Text "Bookmarks")**
        * ファイルブラウザのブックマークをBlenderのテキストエディタで開きます
        * ―(Blender text editor open file browser bookmarks)

* **「3Dビュー」エリア > 「追加」メニュー > 「メッシュ」メニュー**
* **―("3D View" Area > "Add" Menu > "Mesh" Menu)**
    * **四角ポリゴン球**
    * **―(Square Polygon Sphere)**
        * 四角ポリゴンのみで構成された球体メッシュを追加します
        * ―(Add sphere mesh is composed only of quadrilateral polygon)
    * **頂点のみ**
    * **―(Only Vertex)**
        * 1頂点のみのメッシュオブジェクトを3Dカーソルの位置に追加します
        * ―(Only 1 vertex meshes 3D adds to position of cursor)
    * **頂点グループごとに分離**
    * **―(Isolate by vertex groups)**
        * 頂点グループの適用されている部分ごとに分離したメッシュ群を作成します
        * ―(Create separate each part of vertex groups applied mesh group)

* **「情報」エリア > 「レンダー」メニュー**
* **―("Info" Area > "Render" Menu)**
    * **解像度の倍率を設定**
    * **―(Set multi of resolution)**
        * 設定解像度の何パーセントの大きさでレンダリングするか設定します
        * ―(Set to be rendered settings resolution percentage?)
    * **レンダースロットを設定**
    * **―(Set Render Slot)**
        * レンダリング結果を保存するスロットを設定します
        * ―(Sets slot to save rendering results)
    * **スレッド数を切り替え**
    * **―(Switch Use Threads)**
        * レンダリングに使用するCPUのスレッド数を切り替えます
        * ―(Toggles thread number of CPUS used to render)
    * **レンダリング時のサブサーフレベルをまとめて設定**
    * **―(Set Subsurf levels during rendering)**
        * レンダリング時に適用するサブサーフの細分化レベルをまとめて設定します
        * ―(Together sets granularity of Subsurf applied during rendering)
    * **レンダリング時のサブサーフレベルをプレビュー値と同期**
    * **―(Sync preview value when rendering Subsurf levels)**
        * 全オブジェクトのレンダリング時に適用するサブサーフの細分化レベルを、プレビューでのレベルへと設定します
        * ―(Granularity of Subsurf apply when rendering entire object sets level in preview)

* **「情報」エリア > 「ウィンドウ」メニュー**
* **―("Info" Area > "Window" Menu)**
    * **エディタータイプ**
    * **―(Editor Type)**
        * エディタータイプ変更のパイメニューです
        * ―(This is a pie menu of editor type change)
    * **UIの英語・日本語 切り替え**
    * **―(Switch UI English/Japanese)**
        * インターフェイスの英語と日本語を切り替えます
        * ―(Switch interface English, Japan,)

* **「プロパティ」エリア > 「マテリアル」タブ > リスト右の▼**
* **―("Properties" Area > "Material" Tab > List Right ▼)**
    * **割り当てのないマテリアルを削除**
    * **―(Delete Non-assignment Material)**
        * 面に一つも割り当てられてないマテリアルを全て削除します
        * ―(Delete all one assigned to surface material)
    * **マテリアルスロット全削除**
    * **―(Remove all material slots)**
        * このオブジェクトのマテリアルスロットを全て削除します
        * ―(Delete all material slots for this object)
    * **空のマテリアルスロット削除**
    * **―(Remove empty material slots)**
        * このオブジェクトのマテリアルが割り当てられていないマテリアルスロットを全て削除します
        * ―(Delete all material of this object has not been assigned material slots)
    * **裏側を透明にする**
    * **―(Set transparent face back)**
        * メッシュの裏側が透明になるようにシェーダーノードを設定します
        * ―(Sets shader nodes transparently mesh back)
    * **スロットを一番上へ**
    * **―(Slot to Top)**
        * アクティブなマテリアルスロットを一番上に移動させます
        * ―(Active material slots on top moves)
    * **スロットを一番下へ**
    * **―(Slot to Bottom)**
        * アクティブなマテリアルスロットを一番下に移動させます
        * ―(Move active material slot at bottom)

* **「プロパティ」エリア > 「オブジェクトデータ」タブ > シェイプキーリスト右の▼**
* **―("Properties" Area > "Object" Tab > ShapeKeys List Right ▼)**
    * **シェイプキーを複製**
    * **―(Duplicate Shape Key)**
        * アクティブなシェイプキーを複製します
        * ―(Duplicate active shape key)
    * **全てのシェイプにキーフレームを打つ**
    * **―(Insert keyframes to all shapes)**
        * 現在のフレームに、全てのシェイプのキーフレームを挿入します
        * ―(Inserts keyframe for all shapes on current frame)
    * **最上段を選択**
    * **―(Select Top)**
        * 一番上のシェイプキーを選択します
        * ―(Select top shape key)
    * **最下段を選択**
    * **―(Select Bottom)**
        * 一番下のシェイプキーを選択します
        * ―(Select bottom shape key)
    * **現在の形状を保持して全シェイプ削除**
    * **―(Remove all shapes and hold current configuration)**
        * 現在のメッシュの形状を保持しながら全シェイプキーを削除します
        * ―(Remove all shape key while maintaining shape of current mesh)
    * **同名のシェイプキー同士をドライバでリンク**
    * **―(Link shape keys same name by driver)**
        * 他の選択オブジェクトのシェイプキーの動作を、アクティブなオブジェクトにドライバでリンクします
        * ―(Behavior of selection of other shape key drivers link active object)
    * **全シェイプを無効化/有効化**
    * **―(Disable/Enable All Shapes)**
        * 全てのシェイプキーを無効化、もしくは有効化します
        * ―(All shape key to disable or enable the)

* **「プロパティ」エリア > 「オブジェクトデータ」タブ > 頂点グループリスト右の▼**
* **―("Properties" Area > "Object" Tab > VertexGroups List Right ▼)**
    * **空の頂点グループを削除**
    * **―(Delete empty vertex groups)**
        * メッシュにウェイトが割り当てられていない頂点グループを削除します
        * ―(Remove weights assigned to mesh vertex groups)
    * **ミラーの対になる空頂点グループを追加**
    * **―(Add empty mirroring vertex group)**
        * .L .R などミラーの命令規則に従って付けられたボーンの対になる空の新規ボーンを追加します
        * ―(. L... R, add an empty pair of bones according to mandate rule in Miller's new born)
    * **一番上を選択**
    * **―(Select Top)**
        * 頂点グループの一番上の項目を選択します
        * ―(Select item at top of vertex groups)
    * **一番下を選択**
    * **―(Select Bottom)**
        * 頂点グループの一番下の項目を選択します
        * ―(Select item at bottom of vertex groups)
    * **最上段へ**
    * **―(To Top)**
        * アクティブな頂点グループを一番上へ移動させます
        * ―(Move to top active vertex groups)
    * **最下段へ**
    * **―(To Bottom)**
        * アクティブな頂点グループを一番下へ移動させます
        * ―(Move to bottom vertex group active)
    * **特定文字列が含まれる頂点グループ削除**
    * **―(Delete vertex groups contain specific text)**
        * 指定した文字列が名前に含まれている頂点グループを全て削除します
        * ―(Removes all vertex group names contains specified string)

* **「ノードエディター」エリア > 「ノード」メニュー**
* **―("Node Editor" Area > "Node" Menu)**
    * **このシェーダーノードを他マテリアルにコピー**
    * **―(Copy to other material shader node)**
        * 表示しているシェーダーノードを他のマテリアルにコピーします
        * ―(Copies of other material shader nodes are displayed)

* **「ノードエディター」エリア > 「ビュー」メニュー**
* **―("Node Editor" Area > "View" Menu)**
    * **パネル表示切り替え(モードA)**
    * **―(Toggle Panel (mode A))**
        * プロパティ/ツールシェルフの「両方表示」/「両方非表示」をトグルします
        * ―(properties/tool shelf "both display" / "both hide" toggle)
    * **パネル表示切り替え(モードB)**
    * **―(Toggle Panel (mode B))**
        * 「パネル両方非表示」→「ツールシェルフのみ表示」→「プロパティのみ表示」→「パネル両方表示」のトグル
        * ―("Panel both hide" => show only tool shelf => show only properties => "Panel both display" for toggle)
    * **パネル表示切り替え(モードC)**
    * **―(Toggle Panel (mode C))**
        * 「パネル両方非表示」→「ツールシェルフのみ表示」→「プロパティのみ表示」... のトグル
        * ―("Panel both hide" => "show only tool shelf => show only properties. toggle)

* **「プロパティ」エリア > 「オブジェクト」タブ**
* **―("Properties" Area > "Object" Tab)**
    * **オブジェクト名をデータ名に**
    * **―(Object name to data name)**
        * オブジェクト名をリンクしているデータ名に設定します
        * ―(Set data name linked to object name)
    * **データ名をオブジェクト名に**
    * **―(Data name to object name)**
        * データ名をリンクしているオブジェクト名に設定します
        * ―(Sets data linked to object name)
    * **オブジェクト名をコピー**
    * **―(Copy Object Name)**
        * オブジェクト名をクリップボードにコピーします
        * ―(Copy to Clipboard object name)
    * **データ名をコピー**
    * **―(Copy Data Name)**
        * データ名をクリップボードにコピーします
        * ―(Copies data to Clipboard)

* **「プロパティ」エリア > 「オブジェクト」タブ > 「表示」パネル**
* **―("Properties" Area > "Object" Tab > "Display" Panel)**
    * **表示設定をコピー**
    * **―(Copy Display Setting)**
        * この表示設定を他の選択オブジェクトにコピーします
        * ―(Copy selected objects of other display settings)

* **「プロパティ」エリア > 「物理演算」タブ > 「クロス」パネル**
* **―("Properties" Area > "Physics" Tab > "Cloth" Panel)**
    * **クロスの設定をリンク**
    * **―(Link Cloth Setting)**
        * アクティブオブジェクトのクロスシミュレーション設定を、他の選択オブジェクトにコピーします
        * ―(Cloth simulation for active object copies to other selected objects)

* **「プロパティ」エリア > 「物理演算」タブ > 「ダイナミックペイント」パネル**
* **―("Properties" Area > "Physics" Tab > "Dinamic Paint" Panel)**
    * **ダイナミックペイント設定をコピー**
    * **―(Copy Dynamic Paint Settings)**
        * アクティブなオブジェクトのダイナミックペイント設定を、他の選択オブジェクトにコピーします
        * ―(Dynamic paint on an active object copies to other selected objects)

* **「プロパティ」エリア > 「物理演算」タブ > 「フォースフィールド」パネル**
* **―("Properties" Area > "Physics" Tab > "Force Fields" Panel)**
    * **フォースフィールド設定をコピー**
    * **―(Copy ForceField Settings)**
        * アクティブなオブジェクトのフォースフィールド設定を、他の選択オブジェクトにコピーします
        * ―(Copy selection of other force field for active object)

* **「プロパティ」エリア > 「物理演算」タブ > 「剛体」パネル**
* **―("Properties" Area > "Physics" Tab > "Rigid Body" Panel)**
    * **剛体設定をコピー**
    * **―(Copy rigid body setting)**
        * アクティブなオブジェクトの剛体設定を、他の選択オブジェクトにコピーします
        * ―(Copy selected objects of other rigid set of active objects)

* **「プロパティ」エリア > 「物理演算」タブ > 「剛体コンストレイント」パネル**
* **―("Properties" Area > "Physics" Tab > "Rigid Body Constraint" Panel)**
    * **剛体コンストレイント設定をコピー**
    * **―(Copy rigidbody constraints settings)**
        * アクティブなオブジェクトの剛体コンストレイント設定を、他の選択オブジェクトにコピーします
        * ―(Copies selected objects for other rigid constraints on active object)
    * **剛体コンストレイントの制限を初期化**
    * **―(Reset rigid body constraint limits)**
        * アクティブなオブジェクトの剛体コンストレイントの制限設定群を初期化します
        * ―(Initializes rigid constraints of active object limit settings group)
    * **剛体コンストレイントの制限を反転**
    * **―(Invert rigidbody constraints limits)**
        * アクティブなオブジェクトの剛体コンストレイントの制限設定の最小と最大を反転させます
        * ―(Minimum limit settings of rigid constraints of active object and reverses maximum)

* **「プロパティ」エリア > 「物理演算」タブ > 「ソフトボディ」パネル**
* **―("Properties" Area > "Physics" Tab > "Soft Body" Panel)**
    * **ソフトボディ設定をコピー**
    * **―(Copy Soft Body Settings)**
        * アクティブオブジェクトのソフトボディの設定を、他の選択オブジェクトにコピーします
        * ―(Sets active object soft copies to other selected objects)

* **「プロパティ」エリア > ヘッダー**
* **―("Properties" Area > Header)**
    * **プロパティタブを切り替え**
    * **―(Switch Properties Tab)**
        * プロパティのタブを順番に切り替えます
        * ―(Switch properties tab in turn)

* **「プロパティ」エリア > 「レンダー」タブ > 「ベイク」パネル**
* **―("Properties" Area > "Render" Tab > "Bake" Panel)**
    * **ベイク用の画像を作成**
    * **―(New image for bake)**
        * ベイクに使う新規画像を素早く用意可能です
        * ―(New images used to bake quickly, is available)

* **「プロパティ」エリア > 「レンダー」タブ > 「レンダー」パネル**
* **―("Properties" Area > "Render" Tab > "Render" Panel)**
    * **バックグラウンドでレンダリング**
    * **―(Background Rendering)**
        * コマンドラインから現在のblendファイルをレンダリングします
        * ―(Renders current blend file from command line)

* **「プロパティ」エリア > 「シーン」タブ > 「剛体ワールド」パネル**
* **―("Properties" Area > "Scene" Tab > "Rigid Body World" Panel)**
    * **剛体ワールドを作り直す**
    * **―(Recreate RigidBody World)**
        * 設定は維持して剛体ワールドを作り直します
        * ―(Keep setting, recreate rigid world)
    * **剛体ワールドの開始/終了フレームをセット**
    * **―(Set start/end frames rigid body world)**
        * 剛体ワールドの開始/終了フレームをレンダリングの開始/終了フレームへと設定します
        * ―(Start / end frame rigid world of sets to start / end frame rendering)

* **「プロパティ」エリア > 「テクスチャ」タブ > リスト右の▼**
* **―("Properties" Area > "Texture" Tab > List Right ▼)**
    * **テクスチャ名を使用する画像ファイル名に**
    * **―(Image File name to Texture Name)**
        * アクティブなテクスチャの名前を使用している外部画像のファイル名にします
        * ―(file name of external images using name of active texture)
    * **テクスチャスロットを全て空に**
    * **―(Clear all texture slots)**
        * アクティブなマテリアルの全てのテクスチャスロットを空にします
        * ―(Empties all active material texture slots)
    * **最上段へ**
    * **―(To Top)**
        * アクティブなテクスチャスロットを一番上に移動させます
        * ―(Move active texture slot at top)
    * **最下段へ**
    * **―(To Bottom)**
        * アクティブなテクスチャスロットを一番下に移動させます
        * ―(Move active texture slot to bottom)
    * **無効なテクスチャを削除**
    * **―(Remove Invalid Texture)**
        * 無効にしているテクスチャを全て削除します
        * ―(Removes all textures have turned off)
    * **空のテクスチャスロットを切り詰める**
    * **―(Cut empty texture slots)**
        * テクスチャが割り当てられていない空のテクスチャスロットを埋め、切り詰めます
        * ―(No texture is assigned an empty texture slots will be filled, truncated)
    * **ここより下を削除**
    * **―(Delete Below Here)**
        * アクティブなテクスチャスロットより下を、全て削除します
        * ―(Remove all active texture slot below)

* **「プロパティ」エリア > 「テクスチャ」タブ > 「画像」パネル**
* **―("Properties" Area > "Texture" Tab > "Image" Panel)**
    * **テクスチャ画像をUV/画像エディターに表示**
    * **―(Texture images show in UV / image editor)**
        * アクティブなテクスチャに使われている画像を「UV/画像エディター」に表示します
        * ―(Image is used in active texture shows UV / image editor)
    * **このテクスチャでテクスチャペイント**
    * **―(Texture paint by this texture)**
        * アクティブなテクスチャでテクスチャペイントを行います
        * ―(Active texture provides texture paint)

* **「プロパティ」エリア > 「テクスチャ」タブ > 「マッピング」パネル**
* **―("Properties" Area > "Texture" Tab > "Mapping" Panel)**
    * **アクティブなUVを使う**
    * **―(Use Active UV)**
        * メッシュのアクティブなUVを、このスロットで使います
        * ―(Active UV mesh used in this slot)

* **「テキストエディター」エリア > 「テキスト」メニュー**
* **―("Text Editor" Area > "Text" Menu)**
    * **外部エディターで編集**
    * **―(Edit with external editor)**
        * ユーザー設定のファイルタブで設定した外部エディターでテキストを開きます
        * ―(Open text in an external editor you set on files page of custom)

* **メニューに表示されないコマンド**
* **―(Undisplay Commands)**
    * **最後までスクロール**
    * **―(Scroll End)**
        * 画面の一番下までスクロールします
        * ―(Scroll to bottom of screen)

* **「ユーザー設定」エリア > ヘッダー**
* **―("User Prefences" Area > Header)**
    * **ユーザー設定タブを切り替え**
    * **―(Switch user prefences tab)**
        * ユーザー設定のタブを順番に切り替えます
        * ―(Cycles user settings tab)
    * **キーバインド検索**
    * **―(Search Key Bind)**
        * 設定したキーバインドに一致する割り当てを検索します
        * ―(Find matching key bindings you set assignment)
    * **ショートカット検索をクリア**
    * **―(Clear Search Shortcuts)**
        * ショートカット検索に使用した文字列を削除します
        * ―(Remove string used to search for shortcuts)
    * **キーコンフィグを全て閉じる**
    * **―(Close all key configs)**
        * キーコンフィグのメニューを全て折りたたみます
        * ―(Collapses all game menu)
    * **ショートカット一覧をブラウザで閲覧**
    * **―(Show shortcut list by browser)**
        * Blenderの全てのショートカットをブラウザで確認出来ます
        * ―(Can confirm Blender all shortcuts in browser)
    * **最後のコマンドをショートカットに登録**
    * **―(Create Shortcut by Last Command)**
        * 最後に実行したコマンドをショートカットに登録します
        * ―(Last command create shortcut)
    * **割り当ての無いショートカット一覧**
    * **―(Non-Assigning Shortcuts List)**
        * 現在の編集モードでの割り当ての無いキーを「情報」エリアに表示します
        * ―(Information area shows key assignments in current editing mode without)
    * **キーコンフィグをXMLでインポート**
    * **―(Import Key Config XML)**
        * キーコンフィグをXML形式で読み込みます
        * ―(game reads in XML format)
    * **キーコンフィグをXMLでエクスポート**
    * **―(Export Key Config XML)**
        * キーコンフィグをXML形式で保存します
        * ―(Game save in XML format)
    * **展開しているキー割り当てのカテゴリを移動**
    * **―(Move shortcut expanded to other categories)**
        * 展開しているキー割り当てを、他のカテゴリに移動します
        * ―(Move key assignments that expand into other categories)
    * **Blender-Scramble-Addonを更新**
    * **―(Update Blender-Scramble-Addon)**
        * Blender-Scramble-Addonをダウンロード・更新を済ませます
        * ―(Downloads, updates and check out Blender-Scramble-Addon)
    * **「追加項目のオン/オフ」の表示切り替え**
    * **―(Toggle "On/Off Additional Items")**
        * ScrambleAddonによるメニューの末尾の「追加項目のオン/オフ」ボタンの表示/非表示を切り替えます
        * ―(Show or hide turn on/off additional items button at end of menu by ScrambleAddon)

* **「ユーザー設定」エリア > 「ファイル」タブ**
* **―("User Prefences" Area > "File" Tab)**
    * **.blendファイルをこのバージョンに関連付け**
    * **―(.blend file associated with this version)**
        * .blendファイルをこのBlender実行ファイルに関連付けます (WindowsOSのみ)
        * ―((WindowsOS only) associated with Blender running file.blend file)
    * **バックアップをこのバージョンに関連付け**
    * **―(Backup Files with This Blender Version)**
        * .blend1 .blend2 などのバックアップファイルをこのBlender実行ファイルに関連付けます (WindowsOSのみ)
        * ―(associates with Blender running file backup file, such as.blend1.blend2 (WindowsOS only))

* **「3Dビュー」エリア > 「アーマチュア編集」モード > 「W」キー**
* **―("3D View" Area > "Armature Editor" Mode > "W" Key)**
    * **選択ボーンをミラーリング**
    * **―(Select Bones Mirroring)**
        * 選択中のボーンを任意の軸でミラーリングします
        * ―(Mirrored at any axes selected bone)
    * **ボーン名をクリップボードにコピー**
    * **―(Bone name to Clipboard)**
        * アクティブボーンの名前をクリップボードにコピーします
        * ―(Copies Clipboard name of active bone)
    * **ボーン名を正規表現で置換**
    * **―(Replace bone names by regular expression)**
        * (選択中の)ボーン名を正規表現に一致する部分で置換します
        * ―(In bone name (of choice) to match regular expression replace)
    * **反対位置にあるボーンをリネーム**
    * **―(Rename bone symmetry position)**
        * 選択中ボーンのX軸反対側の位置にあるボーンを「○.R ○.L」のように対にします
        * ―(Bone is located opposite X axis selection in bone "1.R longs 1.L ' of so versus the)
    * **ボーンを延長**
    * **―(Extend Bone)**
        * 選択ボーンの方向に新規ボーンを伸ばします
        * ―(Stretch new bone in direction of selected bone)

* **「3Dビュー」エリア > 「アーマチュア編集」モード > 「Shift + W」キー**
* **―("3D View" Area > "Armature Editor" Mode > "Shift + W" Key)**
    * **ボーン名をまとめて設定**
    * **―(Set Bone Names)**
        * 選択中のボーンの名前をまとめて設定します
        * ―(name of selected bone sets together)
    * **カーブボーンをまとめて設定**
    * **―(Set Curve Bones)**
        * 選択中のボーンのカーブボーン設定をします
        * ―(Bones of selected curve born sets)
    * **ロールをまとめて設定**
    * **―(Set Rolls)**
        * 選択中のボーンのロールを設定します
        * ―(Set selected bone rolls)

* **「3Dビュー」エリア > 「アーマチュア編集」モード > 「アーマチュア」メニュー**
* **―("3D View" Area > "Armature Editor" Mode > "Armature" Menu)**
    * **確認無しでボーンを削除**
    * **―(Delete bone without confirm)**
        * ボーンを確認無しで削除します
        * ―(Remove bones without confirm)

* **「3Dビュー」エリア > 「メッシュ編集」モード > 「メッシュ」メニュー**
* **―("3D View" Area > "Mesh Editor" Mode > "Mesh" Menu)**
    * **メッシュ選択モードの切り替え**
    * **―(Switch mesh select mode)**
        * メッシュ選択モードを頂点→辺→面…と切り替えます
        * ―(Mesh selection mode => top => side surface. Switch and)
    * **メッシュ選択モード**
    * **―(Mesh Selection Mode)**
        * メッシュの選択のパイメニューです
        * ―(Mesh select pie menu)
    * **プロポーショナル編集**
    * **―(Proportional Edit)**
        * プロポーショナル編集のパイメニューです
        * ―(Is pie menu proportional edit)

* **「3Dビュー」エリア > 「メッシュ編集」モード > 「X」キー**
* **―("3D View" Area > "Mesh Editor" Mode > "X" Key)**
    * **選択モードと同じ要素を削除**
    * **―(Remove same element to selection mode)**
        * 現在のメッシュ選択モードと同じ要素(頂点・辺・面)を削除します
        * ―(Same mesh selection mode of current element (vertex and side and side) remove)
    * **隠している部分を削除**
    * **―(Remove Hidden Meshes)**
        * 隠している状態のメッシュを全て削除します
        * ―(Delete all are mesh)

* **「3Dビュー」エリア > 「メッシュ編集」モード > 「メッシュ」メニュー > 「表示/隠す」メニュー**
* **―("3D View" Area > "Mesh Editor" Mode > "Mesh" Menu > "Show/Hide" Menu)**
    * **表示/隠すを反転**
    * **―(Invert Show/Hide)**
        * 表示状態と非表示状態を反転させます
        * ―(Invert show or non-show state)
    * **頂点のみを隠す**
    * **―(Hide Only Vertex)**
        * 選択状態の頂点のみを隠して固定します
        * ―(Hide and Fix Selected vertices)
    * **選択しているパーツを隠す**
    * **―(Hide Selected Parts)**
        * 1頂点以上を選択しているメッシュパーツを隠します
        * ―(Hides mesh part has selected more than one top)

* **「3Dビュー」エリア > 「メッシュ編集」モード > 「W」キー**
* **―("3D View" Area > "Mesh Editor" Mode > "W" Key)**
    * **選択頂点の頂点カラーを塗り潰す**
    * **―(Paint out selected vertex color)**
        * 選択中の頂点のアクティブ頂点カラーを指定色で塗り潰します
        * ―(Active vertex colors for selected vertices with specified color fills)
    * **一番上のシェイプを選択**
    * **―(Select shape at top)**
        * リストの一番上にあるシェイプキーを選択します
        * ―(Schipke is at top of list, select)
    * **編集ケージへのモディファイア適用を切り替え**
    * **―(Transition modifiers apply to editing cage)**
        * 編集中のメッシュケージにモディファイアを適用するかを切り替えます
        * ―(Toggles whether to apply modifiers to total en bloc spondylectomy in editing)
    * **ミラーモディファイアを切り替え**
    * **―(Toggle Mirror Modifiers)**
        * ミラーモディファイアが無ければ追加、有れば削除します
        * ―(Delete if not Miller modifier added, Yes)
    * **選択頂点を平均ウェイトで塗り潰す**
    * **―(Fill selected vertices average weight)**
        * 選択頂点のウェイトの平均で、選択頂点を塗り潰します
        * ―(Fills selected vertex, vertices weighted average)

* **「3Dビュー」エリア > 「メッシュ編集」モード > 「Ctrl + V」キー**
* **―("3D View" Area > "Mesh Editor" Mode > "Ctrl + V" Key)**
    * **別オブジェクトに分離 (拡張)**
    * **―(Separate (Advance))**
        * 「別オブジェクトに分離」の拡張メニューを呼び出します
        * ―(Isolate to another object of call extended menu)
    * **選択物 (分離側をアクティブ)**
    * **―(Selected (Activate Isolated-side))**
        * 「選択物で分離」した後に分離した側のエディトモードに入ります
        * ―(After "in choice of separation" enters edit mode for separation side)
    * **選択部を複製/新オブジェクトに**
    * **―(Duplicate Selected parts and to new object)**
        * 選択部分を複製・分離し新オブジェクトにしてからエディトモードに入ります
        * ―(Enters edit mode, replication and selection to new object from)
    * **クイック・シュリンクラップ**
    * **―(Quick Shrinkwrap)**
        * もう1つの選択メッシュに、選択頂点をぺったりとくっつけます
        * ―(Another one you mesh selected vertices pettanko!, glue)

* **「3Dビュー」エリア > 「オブジェクト」モード > 「Ctrl + L」キー**
* **―("3D View" Area > "Object" Mode > "Ctrl + L" Key)**
    * **オブジェクト名を同じに**
    * **―(Sync Object Name)**
        * 他の選択オブジェクトにアクティブオブジェクトの名前をリンクします
        * ―(Link name of active object to other selected objects)
    * **レイヤーを同じに**
    * **―(Set Same Layer)**
        * 他の選択オブジェクトにアクティブオブジェクトのレイヤーをリンクします
        * ―(link active object layers to other selected objects)
    * **オブジェクトの表示設定を同じに**
    * **―(Make same objects display setting)**
        * 他の選択オブジェクトにアクティブオブジェクトの表示パネルの設定をコピーします
        * ―(Copy settings panel of active object to other selected objects)
    * **空のUVマップをリンク**
    * **―(Link empty UV map)**
        * 他の選択オブジェクトにアクティブオブジェクトのUVを空にして追加します
        * ―(Empty, add UV active objects to other selected objects)
    * **アーマチュアの動きをリンク**
    * **―(Link motion of armature)**
        * コンストレイントによって、他の選択アーマチュアにアクティブアーマチュアの動きを真似させます
        * ―(By constraints on other selected armature mimic active armature movement)
    * **変形をリンク**
    * **―(Link Transform)**
        * アクティブオブジェクトの変形情報を、他の選択オブジェクトにコピーします
        * ―(Information of active object copies to other selected objects)

* **「3Dビュー」エリア > 「オブジェクト」モード > 「オブジェクト」メニュー**
* **―("3D View" Area > "Object" Mode > "Object" Menu)**
    * **コピー**
    * **―(Copy)**
        * オブジェクトに関するコピーのパイメニューです
        * ―(Pie object copy is)
    * **オブジェクト対話モード**
    * **―(Object Modes)**
        * オブジェクト対話モードのパイメニューです
        * ―(Is pie menu objects in interactive mode)
    * **サブサーフ設定**
    * **―(Subsurf Setting)**
        * サブサーフのレベルを設定するパイメニューです
        * ―(Is pie menu to set Subsurf levels)
    * **最高描画タイプ**
    * **―(Maximum Draw Type)**
        * 最高描画タイプを設定するパイメニューです
        * ―(Is pie menu to set up drawing type)
    * **確認せずに削除**
    * **―(Delete Without Confirmation)**
        * 削除する時の確認メッセージを表示せずにオブジェクトを削除します
        * ―(Deletes object without displaying confirmation message when deleting)

* **「3Dビュー」エリア > 「オブジェクト」モード > 「Ctrl + A」キー**
* **―("3D View" Area > "Object" Mode > "Ctrl + A" Key)**
    * **位置/回転/拡縮を適用**
    * **―(Apply Location/Rotation/Scale)**
        * オブジェクトの位置/回転/拡縮を適用します
        * ―(Applies to object position / rotation / Pan)

* **「3Dビュー」エリア > 「オブジェクト」モード > 「オブジェクト」メニュー > 「表示/隠す」メニュー**
* **―("3D View" Area > "Object" Mode > "Object" Menu > "Show/Hide" Menu)**
    * **隠したものを表示 (非選択)**
    * **―(Show Hidden (non-select))**
        * 隠していたオブジェクトを再び表示します、選択はしません
        * ―(Does not display objects were hidden again, select)
    * **表示/隠すを反転**
    * **―(Invert Show/Hide)**
        * オブジェクトの表示状態と非表示状態を反転させます
        * ―(Flips object's view state and non-State)
    * **特定の種類のオブジェクトのみを隠す**
    * **―(Hide only type of objects)**
        * 表示されている特定タイプのオブジェクトを隠します
        * ―(Hides object of specific type are displayed)
    * **特定の種類のオブジェクト以外を隠す**
    * **―(Hide except type of objects)**
        * 表示されている特定タイプのオブジェクト以外を隠します
        * ―(Hides object non-specific type that is displayed)

* **「3Dビュー」エリア > 「オブジェクト」モード > 「W」キー**
* **―("3D View" Area > "Object" Mode > "W" Key)**
    * **ウェイト転送**
    * **―(Weight Transfer)**
        * 他の選択中のメッシュからアクティブにウェイトペイントを転送します
        * ―(From mesh during selection of other active forwarding weight paint)
    * **スムーズ/フラットを切り替え**
    * **―(Toggle Smooth/Flat)**
        * 選択中のメッシュオブジェクトのスムーズ/フラット状態を切り替えます
        * ―(Toggles selected mesh object smooth / flat state)
    * **頂点グループの転送**
    * **―(Transfer Vertex Group)**
        * アクティブなメッシュに他の選択メッシュの頂点グループを転送します
        * ―(Transfers to other selected mesh vertex group active mesh)
    * **全頂点の平均ウェイトで塗り潰す**
    * **―(Fill average weight of all vertices)**
        * 全てのウェイトの平均で、全ての頂点を塗り潰します
        * ―(In average weight of all, fills all vertices)
    * **頂点にメタボールをフック**
    * **―(Hook Metaballs)**
        * 選択中のメッシュオブジェクトの頂点部分に新規メタボールを張り付かせます
        * ―(Have made new metaballs to vertices of selected mesh object)
    * **グリースペンシルにメタボール配置**
    * **―(Metaballs to GreasePencil)**
        * アクティブなグリースペンシルに沿ってメタボールを配置します
        * ―(metaballs align with active grease pencil)
    * **メッシュの変形を真似するアーマチュアを作成**
    * **―(Creating an armature to mimic mesh deformation)**
        * アクティブメッシュオブジェクトの変形に追従するアーマチュアを新規作成します
        * ―(Creates new armature to follow active mesh objects)
    * **頂点グループがある頂点位置にボーン作成**
    * **―(Create bone to vertices of vertex groups)**
        * 選択オブジェクトの頂点グループが割り当てられている頂点位置に、その頂点グループ名のボーンを作成します
        * ―(Create vertex group names bone vertices where vertex group of selected objects that are assigned)
    * **厚み付けモディファイアで輪郭線生成**
    * **―(Create line drawing by solidify modifier)**
        * 選択オブジェクトに「厚み付けモディファイア」による輪郭描画を追加します
        * ―(Add to thicken modi contour drawing selection)
    * **選択物のレンダリングを制限**
    * **―(Limit Rendering Selected)**
        * 選択中のオブジェクトをレンダリングしない設定にします
        * ―(setting does not render selected object)
    * **レンダリングするかを「表示/非表示」に同期**
    * **―(Or to render "show / hide" to sync)**
        * 現在のレイヤー内のオブジェクトをレンダリングするかどうかを表示/非表示の状態と同期します
        * ―(Synchronize display / hide status and whether or not to render objects in current layer)
    * **すべての選択制限をクリア**
    * **―(Clear all selected limits)**
        * 全てのオブジェクトの選択不可設定を解除します(逆も可)
        * ―(Removes all non-select settings (vice versa))
    * **非選択物の選択を制限**
    * **―(Limit select to non-selected)**
        * 選択物以外のオブジェクトを選択出来なくします
        * ―(Cannot select object other than selection of)
    * **選択物の選択を制限**
    * **―(Limit Select)**
        * 選択中のオブジェクトを選択出来なくします
        * ―(Can't select selected object)
    * **オブジェクト名を正規表現で置換**
    * **―(Replace object names by regular expression)**
        * 選択中のオブジェクトの名前を正規表現で置換します
        * ―(Name of currently selected object replace with regular expressions)
    * **オブジェクト名とデータ名を同じにする**
    * **―(Sync object name and data name)**
        * 選択中のオブジェクトのオブジェクト名とデータ名を同じにします
        * ―(same object and data names for selected objects)
    * **オブジェクトカラー有効 + 色設定**
    * **―(Enable object color + set color)**
        * 選択オブジェクトのオブジェクトカラーを有効にし、色を設定します
        * ―(Object color of selected object and sets color,)
    * **オブジェクトカラー無効 + 色設定**
    * **―(Disable object color + set color)**
        * 選択オブジェクトのオブジェクトカラーを無効にし、色を設定します
        * ―(To disable object color of selected object, sets color)
    * **モディファイア適用してペアレント作成**
    * **―(Applied Modifiers and Create Parent)**
        * 親オブジェクトのモディファイアを適用してから、親子関係を作成します
        * ―(Create parent/child relationship after applying modifiers of parent object)
    * **カーブからロープ状のメッシュを作成**
    * **―(Create rope-shaped mesh from curves)**
        * アクティブなカーブオブジェクトに沿ったロープや蛇のようなメッシュを新規作成します
        * ―(Creates mesh like rope along curve object is active or snake new)
    * **ベベルオブジェクトを断面に移動**
    * **―(Bevel object move section)**
        * カーブに設定されているベベルオブジェクトを選択カーブの断面へと移動させます
        * ―(Curve beveled objects that move and selection curve section)

* **「3Dビュー」エリア > 「ウェイトペイント」モード > 「ウェイト」メニュー**
* **―("3D View" Area > "Weight Paint" Mode > "Weights" Menu)**
    * **ウェイト同士の合成**
    * **―(Combine Weights)**
        * 選択中のボーンと同じ頂点グループのウェイトを合成します
        * ―(Weight of selected bone and same vertex group merges)
    * **ウェイト同士の減算**
    * **―(Subtraction Weights)**
        * 選択中のボーンと同じ頂点グループのウェイトを減算します
        * ―(Subtracts weight of selected bone and same vertex groups)
    * **全頂点の平均ウェイトで塗り潰す**
    * **―(Fill average weight of all vertices)**
        * 全てのウェイトの平均で、全ての頂点を塗り潰します
        * ―(In average weight of all, fills all vertices)
    * **オブジェクトが重なっている部分を塗る**
    * **―(Paint objects overlap)**
        * 他の選択オブジェクトと重なっている部分のウェイトを塗ります
        * ―(I painted weight of portion that overlaps other selected objects)
    * **頂点グループぼかし**
    * **―(Vertex Group Blur)**
        * アクティブ、もしくは全ての頂点グループをぼかします
        * ―(Blurs active or all vertex groups)

* **「3Dビュー」エリア > 「ポーズ」モード > 「ポーズ」メニュー > 「コンストレイント」メニュー**
* **―("3D View" Area > "Pose" Mode > "Pose" Menu > "Constraints" Menu)**
    * **IK回転制限をコンストレイント化**
    * **―(IK Rotation Limit to Constraints)**
        * IKの回転制限設定をコンストレイントの回転制限設定にコピー
        * ―(Copy rotation constraint restrictions IK rotation restriction settings)

* **「3Dビュー」エリア > 「ポーズ」モード > 「ポーズ」メニュー > 「表示/隠す」メニュー**
* **―("3D View" Area > "Pose" Mode > "Pose" Menu > "Show/Hide" Menu)**
    * **選択しているものを選択不可に**
    * **―(Selected to Unselectible)**
        * 選択しているボーンを選択不可能にします
        * ―(Choose bone has selected impossible)
    * **全ての選択不可を解除**
    * **―(Unlock All Unselect)**
        * 全ての選択不可設定のボーンを選択可能にします
        * ―(non-selection of all bone)

* **「3Dビュー」エリア > 「ポーズ」モード > 「W」キー**
* **―("3D View" Area > "Pose" Mode > "W" Key)**
    * **カスタムシェイプを作成**
    * **―(Create CustomShape)**
        * 選択ボーンのカスタムシェイプを作成します
        * ―(Creates choice bone shape)
    * **ウェイトコピー用メッシュを作成**
    * **―(Create mesh for weight copy)**
        * 選択中のボーンのウェイトコピーで使用するメッシュを作成します
        * ―(Creates mesh to use with copy of selected bone weight)
    * **ボーン名をクリップボードにコピー**
    * **―(Bone name to Clipboard)**
        * アクティブボーンの名前をクリップボードにコピーします
        * ―(Copies Clipboard name of active bone)
    * **チェーン状ボーンをグリースペンシルに沿わせる**
    * **―(Fit chain of bones to grease pencil)**
        * チェーンの様に繋がった選択ボーンをグリースペンシルに沿わせてポーズを付けます
        * ―(Select bones linked like chain of threading to grease pencil, pose)
    * **ボーン名を正規表現で置換**
    * **―(Replace bone names by regular expression)**
        * (選択中の)ボーン名を正規表現に一致する部分で置換します
        * ―(In bone name (of choice) to match regular expression replace)
    * **スローペアレントを設定**
    * **―(Set SlowParent)**
        * 選択中のボーンにスローペアレントを設定します
        * ―(Sets selected bone slow parent)
    * **ボーン名の XXX.R => XXX_R を相互変換**
    * **―(Bone name XXX. R => XXX_R juggling)**
        * ボーン名の XXX.R => XXX_R を相互変換します
        * ―(Bone name XXX. R => conversion XXX_R)
    * **ボーン名の XXX.R => 右XXX を相互変換**
    * **―(Bone names XXX.R => 右XXX)**
        * ボーン名の XXX.R => 右XXX を相互変換します
        * ―(Bone names XXX.R => 右XXX)
    * **ポーズの有効/無効を切り替え**
    * **―(Enable/Disable Pose)**
        * アーマチュアのポーズ位置/レスト位置を切り替えます
        * ―(Toggles pose/rest position of armature)
    * **対のボーンにコンストレイントをコピー**
    * **―(Copy constraints to mirror bone)**
        * 「X.L」なら「X.R」、「X.R」なら「X.L」の名前のボーンへとコンストレイントをコピーします
        * ―("X.L" If "X.R", "X.R" bone "X.L" name copy constraints)
    * **ボーン名の連番を削除**
    * **―(Remove bone name serial number)**
        * 「X.001」など、連番の付いたボーン名から数字を取り除くのを試みます
        * ―(Attempts to get rid of numbers from bone with sequential number, such as "X.001)
    * **物理演算を設定**
    * **―(Set Rigid Body)**
        * 選択中の繋がったボーン群に、RigidBodyによる物理演算を設定します
        * ―(Sets by RigidBody physics led of selected bone set,)
    * **現ポーズを回転制限に**
    * **―(Now pose to rotation limit)**
        * 現在のボーンの回転状態を、IKやコンストレイントの回転制限へと設定します
        * ―(Current bone rotation sets to rotation limit constraints and IK)

* **「3Dビュー」エリア > 「メッシュ編集」モード > 「選択」メニュー**
* **―("3D View" Area > "Mesh Edit" Mode > "Select" Menu)**
    * **X=0の頂点を選択**
    * **―(Select Vertex X=0)**
        * X=0の頂点を選択する
        * ―(Select vertex of X=0)
    * **右半分を選択**
    * **―(Select Right Half)**
        * メッシュの右半分を選択します(その他設定も有)
        * ―(Select right half of mesh (other settings too))

* **「3Dビュー」エリア > 「オブジェクト」モード > 「選択」メニュー**
* **―("3D View" Area > "Object" Mode > "Select" Menu)**
    * **サイズで比較してオブジェクトを選択**
    * **―(Compare size and select objects)**
        * 最大オブジェクトに対して大きい、もしくは小さいオブジェクトを選択します
        * ―(Select maximum objects larger or smaller objects)
    * **アクティブ以外を非選択に**
    * **―(Non-active to Non-select)**
        * アクティブオブジェクト以外の全てを非選択にします
        * ―(Uncheck everything except for active object)
    * **同じ名前のオブジェクトを選択**
    * **―(Select object same name)**
        * アクティブなオブジェクトと同じ名前 (X X.001 X.002など) の可視オブジェクトを選択します
        * ―(Select visible object of active object with same name, such as (X.001 X X.002))
    * **同じマテリアル構造のオブジェクトを選択**
    * **―(Select objects of same material structure)**
        * アクティブなオブジェクトのマテリアル構造と同じ可視オブジェクトを選択します
        * ―(Select active object material structure and same visible objects)
    * **同じモディファイア構造のオブジェクトを選択**
    * **―(Select same modifier structure object)**
        * アクティブなオブジェクトのモディファイア構造が同じ可視オブジェクトを選択します
        * ―(Select same modifier of active objects visible objects)
    * **同じサブサーフレベルのオブジェクトを選択**
    * **―(Select same subsurf level object)**
        * アクティブなオブジェクトのサブサーフレベルが同じ可視オブジェクトを選択します
        * ―(Select Subsurf levels of active objects have same visible objects)
    * **同じアーマチュアで変形しているオブジェクトを選択**
    * **―(Select objects that transform in same armature)**
        * アクティブなオブジェクトと同じアーマチュアで変形している可視オブジェクトを選択します
        * ―(Select visible objects are transformed in an active object with same armature)
    * **サイズで比較してオブジェクトを選択**
    * **―(Compare size and select objects)**
        * アクティブオブジェクトより大きい、もしくは小さいオブジェクトを追加選択します
        * ―(Greater than active object, or select additional small objects)
    * **面のあるメッシュを選択**
    * **―(Select face exist mesh)**
        * 面が1つ以上あるメッシュを選択します
        * ―(Select mesh more than one face)
    * **辺のみのメッシュを選択**
    * **―(Select edge only mesh)**
        * 面が無く、辺のみのメッシュを選択します
        * ―(Terms, select only side mesh)
    * **頂点のみのメッシュを選択**
    * **―(Select only vertices of mesh)**
        * 面と辺が無く、頂点のみのメッシュを選択します
        * ―(Surfaces and edges, select mesh vertices only)
    * **頂点すら無いメッシュを選択**
    * **―(Select mesh even non vertex)**
        * 面と辺と頂点が無い空のメッシュオブジェクトを選択します
        * ―(Surface and edge and select mesh object vertex is not empty)

* **「3Dビュー」エリア > 「ポーズ」モード > 「選択」メニュー**
* **―("3D View" Area > "Pose" Mode > "Select" Menu)**
    * **連番の付いたボーンを選択**
    * **―(Select Numbered Bone)**
        * X.001 のように番号の付いた名前のボーンを選択します
        * ―(Select bones with number names (example x.001))
    * **対称のボーンへ選択を移動**
    * **―(Symmetrical bones move select)**
        * X.Rを選択中ならX.Lへ選択を変更、X.LならX.Rへ
        * ―(If you select X.R change selection to X.L, X.L if to X.R)
    * **同じコンストレイントのボーンを選択**
    * **―(Select bone same constraints)**
        * アクティブボーンと同じ種類のコンストレイントを持ったボーンを追加選択します
        * ―(Select additional bone with active bone and same kind of constraint)
    * **同じ名前のボーンを選択**
    * **―(Select bone of same name)**
        * X X.001 X.002 などのボーン名を同じ名前とみなして選択します
        * ―(Select bones same names (example X X.001 X.002))
    * **名前が対称のボーンを追加選択**
    * **―(Select add name symmetrical bone)**
        * X.Rを選択中ならX.Lも追加選択、X.LならX.Rも選択
        * ―(If you select X.R X.L also selected X.R X.L you select additional)
    * **ボーンの末端まで選択**
    * **―(Select end of bone)**
        * 選択ボーンの子 → 子ボーンの子...と最後まで選択していきます
        * ―(Select bones child-child child's bones. And we will select to end)
    * **ボーンの根本まで選択**
    * **―(Select root of bone)**
        * 選択ボーンの親 → 親ボーンの親...と最後まで選択していきます
        * ―(Choice bones parent => parent of parent bone. And we will select to end)
    * **ボーンの経路を選択**
    * **―(Select path of bones)**
        * 2つの選択ボーンの経路を選択します
        * ―(Select bones path)
    * **右半分を選択**
    * **―(Select Right Half)**
        * ボーン群の右半分を選択します(その他設定も有り)
        * ―(Select right half of bone (other settings are also available))
    * **ボーンとその経路を選択**
    * **―(Select bone and path)**
        * カーソル部分のボーンを選択し、そこまでの経路も選択します
        * ―(Select path to it, select cursor part bone and)

* **「3Dビュー」エリア > 「Shift + S」キー**
* **―("3D View" Area > "Shift + S" Key)**
    * **メッシュに3Dカーソルをスナップ**
    * **―(3D Cursor Snap to Mesh)**
        * マウス下のメッシュ面上に3Dカーソルを移動させます(ショートカットに登録してお使い下さい)
        * ―((Please use shortcuts) mesh surface under mouse move 3D cursor)
    * **視点位置に3Dカーソル移動**
    * **―(3D cursor to view)**
        * 視点の中心位置に3Dカーソルを移動させます
        * ―(Move 3D cursor to location of center point of)
    * **3Dカーソルを非表示に(遥か遠くに)**
    * **―(Hide 3D Cursor (move far))**
        * 3Dカーソルを遥か遠くに移動させて非表示のように見せかけます
        * ―(Pretend to hide 3D cursor to move far far away)

* **「3Dビュー」エリア > 「メッシュ編集」モード > 「U」キー**
* **―("3D View" Area > "Mesh Edit" Mode > "U" Key)**
    * **他のUVからコピー**
    * **―(Copy from other UV)**
        * 選択部分のアクティブなUV展開を、他のUVからコピーしてきます
        * ―(Active UV unwrapping of selection can be copied from other UV)

* **「3Dビュー」エリア > 「ビュー」メニュー**
* **―("3D View" Area > "View" Menu)**
    * **グローバルビュー/ローカルビュー(非ズーム)**
    * **―(Global / local view (non-zoom))**
        * 選択したオブジェクトのみを表示し、視点の中央に配置します(ズームはしません)
        * ―(Displays only selected objects and centered point of view doesn't (zoom))
    * **パネル表示切り替え(モードA)**
    * **―(Toggle Panel (mode A))**
        * プロパティ/ツールシェルフの「両方表示」/「両方非表示」をトグルします
        * ―(properties/tool shelf "both display" / "both hide" toggle)
    * **パネル表示切り替え(モードB)**
    * **―(Toggle Panel (mode B))**
        * 「パネル両方非表示」→「ツールシェルフのみ表示」→「プロパティのみ表示」→「パネル両方表示」のトグル
        * ―("Panel both hide" => show only tool shelf => show only properties => "Panel both display" for toggle)
    * **パネル表示切り替え(モードC)**
    * **―(Toggle Panel (mode C))**
        * 「パネル両方非表示」→「ツールシェルフのみ表示」→「プロパティのみ表示」... のトグル
        * ―("Panel both hide" => "show only tool shelf => show only properties. toggle)
    * **シェーディング切り替え(モードA)**
    * **―(Shading Switch (Mode A))**
        * シェーディングを 「ワイヤーフレーム」→「ソリッド」→「テクスチャ」... と切り替えていきます
        * ―("Wireframe", "solid" => "texture" shading... We will switch)
    * **プリセットビュー**
    * **―(Preset View)**
        * プリセットビュー(テンキー1,3,7とか)のパイメニューです
        * ―(Is pie menu of preset views or (NUMPAD 1, 3, 7))
    * **シェーディング切り替え**
    * **―(Shading Switch)**
        * シェーディング切り替えパイメニューです
        * ―(Is shading switch pie)
    * **レイヤーのパイメニュー**
    * **―(Layer Pie Menu)**
        * レイヤー表示切り替えのパイメニューです
        * ―(Is pie menu toggle layer visibility)
    * **パネル切り替えのパイメニュー**
    * **―(Switch panel pie menu)**
        * パネル表示切り替えのパイメニューです
        * ―(Toggle panel pie menu)

* **「3Dビュー」エリア > 「視点を揃える」メニュー**
* **―("3D View" Area > "View" Menu > "Align View" Menu)**
    * **選択部分を表示 (非ズーム)**
    * **―(Show Selected (non-zoom))**
        * 選択中の物に3D視点の中心を合わせます(ズームはしません)
        * ―(Selected ones over center of 3D perspective not (zoom))
    * **視点を原点に**
    * **―(Viewpoint at Origin)**
        * 3Dビューの視点を座標の中心に移動します
        * ―(3D view perspective moves in center of coordinates)
    * **選択+視点の中心に**
    * **―(Select and Set view center)**
        * マウス下の物を選択し視点の中心にします (Shiftを押しながらで追加選択)
        * ―(Select object under mouse, in heart of point of view (SHIFT while additional choices))
    * **メッシュに視点をスナップ**
    * **―(Snap view to mesh)**
        * マウス下のメッシュ面上に視点の中心を移動させます(ショートカットに登録してお使い下さい)
        * ―((Please use shortcuts) move center point of view mesh surface under mouse)
    * **ビューの反対側に**
    * **―(Invert View)**
        * 現在のビューの逆側へ回りこみます
        * ―(This reverses present view)
    * **視点と3Dカーソルを原点に**
    * **―(3D cursor with viewpoint at origin)**
        * 視点と3Dカーソルの位置を原点(XYZ=0.0)に移動させます
        * ―(Perspective and 3D cursor position move to starting point (XYZ=0.0))
    * **メッシュに視点と3Dカーソルをスナップ**
    * **―(Snap mesh view and 3D cursor)**
        * マウス下のメッシュ面上に視点と3Dカーソルを移動させます (ショートカットに登録してお使い下さい)
        * ―((Please use shortcuts) move viewpoint and 3D cursor mesh surface under mouse)

* **「3Dビュー」エリア > 「視点を揃える」メニュー > 「アクティブに視点を揃える」メニュー**
* **―("3D View" Area > "View" Menu > "Align View" Menu > "Align View to Active" Menu)**
    * **面を正面から見る**
    * **―(View Front)**
        * 選択中の面の法線方向から面を注視します
        * ―(watch face from selected surface normal direction)

* **「3Dビュー」エリア > プロパティ > レイヤーボタンがあるパネル**
* **―("3D View" Area > Properties > Layer Buttons Panel)**
    * **グループで表示/非表示を切り替え**
    * **―(Toggle Show/Hide Groups)**
        * 所属しているグループで表示/非表示を切り替えます
        * ―(Switch Show / Hide group has)

* **「3Dビュー」エリア > 「テクスチャペイント」モード > ツールシェルフ > 「スロット」パネル**
* **―("3D View" Area > "Texture Paint" Mode > Tool Shelf > "Slots" Panel)**
    * **アクティブなテクスチャスロットを塗る**
    * **―(Paint Active Texture Slot)**
        * アクティブなペイントスロットをアクティブなテクスチャスロットにします
        * ―(active texture slot slot active paint)

* **「UV/画像エディター」エリア > 「画像」メニュー**
* **―("UV/Image Editor" Area > "Image" Menu)**
    * **クイック編集 (拡張)**
    * **―(Quick Edit (Advance))**
        * ユーザー設定のファイルタブで設定した追加の外部エディターでクイック編集を行います
        * ―(Do quick editing in an external editor of additional files page of custom)

* **「3Dビュー」エリア > プロパティ > 「ビュー」パネル**
* **―("3D View" Area > Properties > "View" Panel)**
    * **視点のセーブ**
    * **―(Save View)**
        * 現在の3Dビューの視点をセーブします
        * ―(Save current 3D view perspective)
    * **視点のロード**
    * **―(Load View)**
        * 現在の3Dビューに視点をロードします
        * ―(Load to current 3D view perspective)
    * **視点セーブを破棄**
    * **―(Delete View Save)**
        * 全ての視点セーブデータを削除します
        * ―(Removes all view save data)

# ライセンス (License)
Copyright (c) 2015 saidenka.
All rights reserved.

Redistribution and use in source and binary forms are permitted
provided that the above copyright notice and this paragraph are
duplicated in all such forms and that any documentation,
advertising materials, and other materials related to such
distribution and use acknowledge that the software was developed
by the saidenka.  The name of the
saidenka may not be used to endorse or promote products derived
from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED `AS IS'' AND WITHOUT ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
